#!/usr/bin/env python3
"""
End-to-end tests for the bmad-samd-qms plugin.

Each test builds a throw-away project in a temporary directory, runs the plugin's own scripts
with a fixed set of answers (tests/fixtures/answers.json), and checks the result. The wiring
tests run BMAD's own resolver, so they prove what BMAD will load, not what the plugin meant
to write. They need a BMAD installation: set BMAD_PROJECT to a project where BMAD is
installed (it must contain _bmad/scripts/resolve_customization.py and
.claude/skills/<skill>/customize.toml for the wired skills). Without it those tests are
skipped, and the run says so.

  BMAD_PROJECT=/path/to/a/bmad/project python3 -m unittest discover -s tests -v

Python 3.11+ (tomllib); pyyaml for merge-config.py.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILL = PLUGIN / "skills" / "qms-init"
SCRIPTS = SKILL / "scripts"
TEMPLATES = PLUGIN / "qms-templates"
WIRING = SKILL / "assets" / "wiring.toml"
ANSWERS = PLUGIN / "tests" / "fixtures" / "answers.json"
BMAD = Path(os.environ["BMAD_PROJECT"]) if os.environ.get("BMAD_PROJECT") else None


def run(script, *args):
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                            capture_output=True, text=True)
    return result


def wired_skills():
    with open(WIRING, "rb") as f:
        return tomllib.load(f)["skills"]


class PluginTest(unittest.TestCase):

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="samd-qms-test-"))
        (self.root / "_bmad").mkdir()

    def tearDown(self):
        shutil.rmtree(self.root)

    def scaffold(self):
        result = run("scaffold-qms.py", "--project-root", self.root, "--templates-dir", TEMPLATES,
                     "--answers", ANSWERS, "--skip-customized")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def wire(self):
        result = run("wire-workflows.py", "--project-root", self.root, "--wiring", WIRING)
        return result.returncode, json.loads(result.stdout)

    # --- the QMS documents -------------------------------------------------------------

    def test_scaffold_creates_every_document_from_the_answers(self):
        report = self.scaffold()
        templates = sorted(str(p.relative_to(TEMPLATES))[:-5] for p in TEMPLATES.rglob("*.tmpl"))
        self.assertEqual(sorted(report["created"]), templates)
        for rel in templates:
            text = (self.root / "qms" / rel).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\{\{[a-z_]+\}\}", f"{rel} keeps a placeholder")
        dod = (self.root / "qms" / "definition-of-done.md").read_text(encoding="utf-8")
        self.assertIn("TestDevice", (self.root / "qms" / "README.md").read_text(encoding="utf-8"))
        self.assertTrue(dod.strip(), "the definition of done is empty")

    def test_a_rerun_never_overwrites_an_edited_document(self):
        self.scaffold()
        dod = self.root / "qms" / "definition-of-done.md"
        dod.write_text("# Our own definition of done\n", encoding="utf-8")
        report = self.scaffold()
        self.assertEqual(dod.read_text(encoding="utf-8"), "# Our own definition of done\n")
        self.assertIn("definition-of-done.md", report["skipped_customized"])

    # --- registration ------------------------------------------------------------------

    def test_setup_registers_the_module_with_the_answers(self):
        result = run("merge-config.py", "--config-path", self.root / "_bmad" / "config.yaml",
                     "--user-config-path", self.root / "_bmad" / "config.user.yaml",
                     "--module-yaml", SKILL / "assets" / "module.yaml", "--answers", ANSWERS)
        self.assertEqual(result.returncode, 0, result.stderr)
        import yaml
        config = yaml.safe_load((self.root / "_bmad" / "config.yaml").read_text(encoding="utf-8"))
        self.assertIn("samd", config)
        self.assertEqual(config["samd"]["device_name"], "TestDevice")

    # --- the wiring --------------------------------------------------------------------

    def test_every_wired_workflow_gets_its_own_file(self):
        code, report = self.wire()
        self.assertEqual(code, 0, report)
        for skill in wired_skills():
            self.assertTrue((self.root / "_bmad" / "custom" / f"{skill}.toml").exists(), skill)

    def test_a_second_wiring_changes_nothing(self):
        self.wire()
        code, report = self.wire()
        self.assertEqual(code, 0)
        self.assertEqual(report["written"], [])
        self.assertEqual(sorted(report["unchanged"]), sorted(wired_skills()))

    def test_the_wiring_never_overwrites_a_teams_own_file(self):
        custom = self.root / "_bmad" / "custom"
        custom.mkdir(parents=True)
        own = custom / "bmad-dev-story.toml"
        own.write_text('[workflow]\npersistent_facts = ["file:{project-root}/our-rules.md"]\n',
                       encoding="utf-8")
        code, report = self.wire()
        self.assertEqual(code, 1)
        self.assertEqual([r["skill"] for r in report["refused"]], ["bmad-dev-story"])
        self.assertIn("our-rules.md", own.read_text(encoding="utf-8"))

    @unittest.skipUnless(BMAD, "set BMAD_PROJECT to run the wiring through BMAD's own resolver")
    def test_bmads_own_resolver_loads_the_qms_into_every_wired_workflow(self):
        resolver = BMAD / "_bmad" / "scripts" / "resolve_customization.py"
        self.assertTrue(resolver.exists(), f"no resolver at {resolver}")
        (self.root / "_bmad" / "scripts").mkdir()
        shutil.copy(resolver, self.root / "_bmad" / "scripts")
        self.scaffold()
        code, report = self.wire()
        self.assertEqual(code, 0, report)
        for skill, entry in wired_skills().items():
            source = BMAD / ".claude" / "skills" / skill
            if not (source / "customize.toml").exists():
                self.fail(f"{skill}: not installed in {BMAD}, so its wiring cannot be checked")
            target = self.root / ".claude" / "skills" / skill
            target.mkdir(parents=True)
            shutil.copy(source / "customize.toml", target)
            result = subprocess.run([sys.executable, str(self.root / "_bmad" / "scripts" /
                                     "resolve_customization.py"), "--skill", str(target),
                                     "--key", "workflow.persistent_facts"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            facts = json.loads(result.stdout).get("workflow.persistent_facts", [])
            for fact in entry["facts"]:
                self.assertIn(f"file:{{project-root}}/{fact}", facts, f"{skill} does not load {fact}")
                self.assertTrue((self.root / fact).exists(), f"{skill} loads {fact}, which setup never creates")


if __name__ == "__main__":
    unittest.main(verbosity=2)
