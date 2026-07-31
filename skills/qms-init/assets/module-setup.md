# SaMD QMS — Module Setup

This file is loaded when:
- The user runs `/qms-init` with `setup` or `configure`
- The module is not yet registered in `{project-root}/_bmad/config.yaml`

## Overview

Registers the `samd` module and scaffolds the `qms/` directory from templates.
Writes three files and patches a fourth:

- `{project-root}/_bmad/config.yaml` — module registration + wizard answers
- `{project-root}/_bmad/config.user.yaml` — personal settings (user_name, language)
- `{project-root}/_bmad/module-help.csv` — QMS capability entries for bmad-help
- `{project-root}/_bmad/custom/config.toml` — **BMAD workflow wiring** (persistent_facts for every skill)

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
  --answers {temp-file}
```

The script instantiates every `*.tmpl` file in `qms-templates/` by substituting
`{{placeholder}}` tokens with wizard answers, and writes the results to `{project-root}/qms/`.
Existing files are NOT overwritten (safe to re-run after manual edits).

## Step 5 — Wire BMAD workflows

Patch `{project-root}/_bmad/custom/config.toml` to inject QMS files into `persistent_facts`
for the key BMAD skills. Read the file first; if it already has a `# [samd-qms-wiring]` block,
replace it. Otherwise append it.

The block to write:

```toml
# [samd-qms-wiring] — managed by bmad-samd-qms plugin. Do not edit this block manually.
# Remove the block and re-run /qms-init configure to regenerate.

[skills.bmad-create-prd.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/constraints-register.md",
  "file:{project-root}/qms/regulatory/intended-use.md",
]

[skills.bmad-create-architecture.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/constraints-register.md",
  "file:{project-root}/qms/requirements/traceability.md",
]

[skills.bmad-create-epics-and-stories.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/constraints-register.md",
]

[skills.bmad-create-story.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/constraints-register.md",
  "file:{project-root}/qms/requirements/traceability.md",
  "file:{project-root}/qms/risk/risk-register.md",
]

[skills.bmad-dev-story.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/constraints-register.md",
  "file:{project-root}/qms/soup-register.md",
  "file:{project-root}/qms/risk/risk-register.md",
]

[skills.bmad-code-review.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/requirements/traceability.md",
]

[skills.bmad-retrospective.workflow]
persistent_facts = [
  "file:{project-root}/qms/definition-of-done.md",
  "file:{project-root}/qms/open-items.md",
]
# [/samd-qms-wiring]
```

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
