# SaMD QMS — Module Setup

This file is loaded when:
- The user runs `/qms-init` with `setup` or `configure`
- The module is not yet registered in `{project-root}/_bmad/config.yaml`

## Overview

Registers the `samd` module and scaffolds the `qms/` directory from templates.
Writes these files:

- `{project-root}/_bmad/config.yaml` — module registration + wizard answers
- `{project-root}/_bmad/config.user.yaml` — personal settings (user_name, language)
- `{project-root}/_bmad/module-help.csv` — QMS capability entries for bmad-help
- `{project-root}/_bmad/custom/<skill>.toml` — **BMAD workflow wiring**, one file per QMS-relevant workflow (persistent_facts)

## Step 1 — Check existing config

Read `./assets/module.yaml` for module metadata.
Check if `{project-root}/_bmad/config.yaml` has a `samd:` section — if yes, this is a reconfigure.

## Step 2 — Collect configuration

Ask the user for values using the `prompt` fields in `./assets/module.yaml`.
Show all questions at once, defaults in brackets. Present single-select fields as numbered lists.
Multi-select fields: show as checkboxes — the user can say "1 and 2" or "US and EU".
Confirm fields: show as Yes/No.

Required fields: device_name, manufacturer_name, intended_use_summary.

## Step 3 — Write config files

Write a temp JSON `{"core": {...}, "module": {...}}` with collected answers.
Resolve `{project-root}` to the actual project root in all path arguments (NOT in config values).

Run in parallel:
```bash
python3 ./scripts/merge-config.py \
  --config-path "{project-root}/_bmad/config.yaml" \
  --user-config-path "{project-root}/_bmad/config.user.yaml" \
  --module-yaml ./assets/module.yaml \
  --answers {temp-file}

python3 ./scripts/merge-help-csv.py \
  --target "{project-root}/_bmad/module-help.csv" \
  --source ./assets/module-help.csv \
  --module-code samd
```

## Step 4 — Scaffold the qms/ directory

Run the scaffold script, passing all collected wizard values as JSON:

```bash
python3 ./scripts/scaffold-qms.py \
  --project-root "{project-root}" \
  --templates-dir "./../../qms-templates" \
  --answers {temp-file} \
  --skip-customized
```

The script instantiates every `*.tmpl` file in `qms-templates/` by substituting
`{{placeholder}}` tokens with wizard answers, and writes the results to `{project-root}/qms/`.
Existing files are NOT overwritten (safe to re-run after manual edits).

## Step 5 — Wire BMAD workflows

Run the wiring script. It writes one `{project-root}/_bmad/custom/<skill>.toml` per entry of
`./assets/wiring.toml`, with the QMS documents as `persistent_facts` — the file BMAD's
`_bmad/scripts/resolve_customization.py` actually reads for a workflow (`[skills.*]` sections
in `_bmad/custom/config.toml` are never read for workflows: that was the 2026 wiring defect).

```bash
python3 ./scripts/wire-workflows.py \
  --project-root "{project-root}" \
  --wiring ./assets/wiring.toml
```

The script never overwrites a `<skill>.toml` it did not write; it reports such a file as
`refused` and exits 1. Show the refused files to the user and ask how to merge them.

Then verify each wired skill with BMAD's own resolver — the QMS files must appear:

```bash
uv run {project-root}/_bmad/scripts/resolve_customization.py \
  --skill {project-root}/.claude/skills/<skill> --key workflow.persistent_facts
```

The same checks run automatically in `tests/test_plugin.py`.

## Step 6 — Create output directories

Create `{project-root}/qms/` and all subdirectories listed in `./assets/module.yaml` under `directories`.

## Step 7 — Confirm

Display:
- Config values written
- Files scaffolded (list of qms/ files created)
- BMAD skills wired (list of skills that now load QMS persistent_facts)

Then display the `module_greeting` from `./assets/module.yaml`.

## Return to skill

Setup complete. Resume normal skill activation.
