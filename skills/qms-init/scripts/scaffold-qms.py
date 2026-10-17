#!/usr/bin/env python3
"""
scaffold-qms.py — instantiate SaMD QMS templates into a project.

Usage:
  python3 scaffold-qms.py \
    --project-root /path/to/project \
    --templates-dir /path/to/qms-templates \
    --answers /path/to/answers.json \
    [--skip-customized]   # skip files that no longer contain {{ tokens (user-edited)

The answers JSON must contain at minimum:
  {
    "module": {
      "device_name": "...",
      "manufacturer_name": "...",
      "intended_use_summary": "...",
      "clinical_domain": "...",
      "fda_class": "...",
      "eu_mdr_class": "...",
      "iec62304_class": "...",
      "phi_handling": true|false,
      "clinician_confirmed": true|false,
      "jurisdiction": ["US", "EU"],
      "source_control": "...",
      "artifact_repo": "..."
    },
    "core": {
      "project_name": "...",
      "user_name": "..."
    }
  }
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path


def load_answers(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    module = data.get("module", {})
    core = data.get("core", {})
    # Flatten into a single substitution map
    subs = {
        "device_name": module.get("device_name", "MyDevice"),
        "manufacturer_name": module.get("manufacturer_name", "My Company Inc."),
        "intended_use_summary": module.get("intended_use_summary", "[FILL IN INTENDED USE]"),
        "clinical_domain": module.get("clinical_domain", "general"),
        "fda_class": module.get("fda_class", "II-510k"),
        "eu_mdr_class": module.get("eu_mdr_class", "IIa"),
        "iec62304_class": module.get("iec62304_class", "B"),
        "phi_handling": "yes" if module.get("phi_handling", True) else "no",
        "clinician_confirmed": "yes" if module.get("clinician_confirmed", True) else "no",
        "jurisdiction": ", ".join(module.get("jurisdiction", ["US", "EU"])),
        "source_control": module.get("source_control", "git"),
        "artifact_repo": module.get("artifact_repo", "internal-artifact-repo"),
        "project_name": core.get("project_name", "MyProject"),
        "user_name": core.get("user_name", ""),
        "year": str(date.today().year),
        "date": date.today().isoformat(),
    }
    # Derived convenience values
    subs["fda_class_label"] = {
        "II-510k": "Class II — 510(k)",
        "II-denovo": "Class II — De Novo",
        "III-PMA": "Class III — PMA",
        "I-exempt": "Class I — Exempt",
        "none": "N/A",
    }.get(subs["fda_class"], subs["fda_class"])
    subs["eu_mdr_class_label"] = {
        "I": "Class I",
        "IIa": "Class IIa",
        "IIb": "Class IIb",
        "III": "Class III",
        "none": "N/A",
    }.get(subs["eu_mdr_class"], subs["eu_mdr_class"])
    subs["iec62304_class_label"] = {
        "A": "Class A (no injury possible)",
        "B": "Class B (non-serious injury possible)",
        "C": "Class C (serious injury or death possible)",
    }.get(subs["iec62304_class"], subs["iec62304_class"])
    return subs


def substitute(text: str, subs: dict) -> str:
    for key, value in subs.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def has_placeholders(text: str) -> bool:
    return bool(re.search(r"\{\{[a-z_]+\}\}", text))


def scaffold(project_root: Path, templates_dir: Path, subs: dict, skip_customized: bool):
    qms_root = project_root / "qms"
    created, skipped, already_customized = [], [], []

    for tmpl_path in sorted(templates_dir.rglob("*.tmpl")):
        rel = tmpl_path.relative_to(templates_dir)
        # Strip the .tmpl suffix for the output filename
        out_rel = Path(str(rel)[:-5])  # remove .tmpl
        out_path = qms_root / out_rel

        out_path.parent.mkdir(parents=True, exist_ok=True)

        tmpl_text = tmpl_path.read_text(encoding="utf-8")
        out_text = substitute(tmpl_text, subs)

        if out_path.exists():
            existing = out_path.read_text(encoding="utf-8")
            # A file with no {{ tokens left has been customized: never overwrite it,
            # with or without --skip-customized (setup promises existing files are safe).
            if not has_placeholders(existing):
                already_customized.append(str(out_rel))
                continue
            # File exists but still has placeholders — overwrite with fresh substitution
            out_path.write_text(out_text, encoding="utf-8")
            skipped.append(str(out_rel))  # "updated"
        else:
            out_path.write_text(out_text, encoding="utf-8")
            created.append(str(out_rel))

    return created, skipped, already_customized


def main():
    parser = argparse.ArgumentParser(description="Scaffold SaMD QMS templates into a project")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--templates-dir", required=True)
    parser.add_argument("--answers", required=True)
    parser.add_argument("--skip-customized", action="store_true",
                        help="Skip files that no longer contain {{ tokens (user-edited)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    templates_dir = Path(args.templates_dir).resolve()

    if not templates_dir.exists():
        print(json.dumps({"status": "error", "message": f"templates-dir not found: {templates_dir}"}))
        sys.exit(1)

    subs = load_answers(args.answers)
    created, updated, customized = scaffold(project_root, templates_dir, subs, args.skip_customized)

    print(json.dumps({
        "status": "success",
        "qms_root": str(project_root / "qms"),
        "created": created,
        "updated": updated,
        "skipped_customized": customized,
    }, indent=2))


if __name__ == "__main__":
    main()
