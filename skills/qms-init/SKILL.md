---
name: qms-init
description: Scaffold a regulation-aligned SaMD QMS and wire it into every BMAD workflow. Supports FDA 21 CFR 820 / IEC 62304 / ISO 14971 / EU MDR. Run once per project.
---

# SaMD QMS Init

## On Activation

### 1. Check for setup/configure argument

If the user passed `setup`, `configure`, or `install` as an argument — OR if
`{project-root}/_bmad/config.yaml` does NOT contain a `samd:` section — load
`./assets/module-setup.md` and complete registration before proceeding.

The `setup`/`configure` argument always triggers `./assets/module-setup.md`
regardless of whether the module is already registered (for reconfiguration).

### 2. Load config (if already registered)

If the module is registered, read `{project-root}/_bmad/config.yaml` (samd section)
and `{project-root}/_bmad/config.user.yaml` for personal settings.

Resolve:
- `samd.device_name`
- `samd.manufacturer_name`
- `samd.fda_class`
- `samd.eu_mdr_class`
- `samd.iec62304_class`
- `samd.phi_handling`
- `samd.clinician_confirmed`
- `samd.jurisdiction`

### 3. Greet

Greet the user, then offer the following actions:

1. **Re-run setup** — reconfigure wizard answers and re-scaffold
2. **Validate QMS** — check that required files exist and contain required sections
3. **Show QMS status** — list files in qms/ with a completeness indicator
4. **Update templates** — apply newer template versions without overwriting customized files
5. **Exit**

---

## Validate QMS (action 2)

Check for required files. For each, report PRESENT / MISSING / STUB (file exists but contains
only placeholder text):

**Required for any SaMD project:**
- `qms/README.md`
- `qms/definition-of-done.md`
- `qms/constraints-register.md`
- `qms/soup-register.md`
- `qms/open-items.md`
- `qms/regulatory/intended-use.md`
- `qms/regulatory/iec-62304-software-file.md`
- `qms/risk/risk-management-file.md`
- `qms/risk/risk-register.md`
- `qms/requirements/traceability.md`

**Required if jurisdiction includes US:**
- `qms/regulatory/fda-classification-rationale.md`
- `qms/regulatory/predicate-analysis.md` (if 510k)
- `qms/regulatory/cybersecurity-file.md`
- `qms/regulatory/submission-toc.md`

**Required if jurisdiction includes EU:**
- `qms/regulatory/gspr-checklist.md`
- `qms/regulatory/clinical-evaluation-plan.md`
- `qms/regulatory/pms-plan.md`

**Required if phi_handling = true:**
- Data minimization and encryption controls documented in `qms/constraints-register.md`

Report overall readiness: READY / PARTIAL / INCOMPLETE.

---

## Show QMS status (action 3)

List all files under `{project-root}/qms/`, grouped by subdirectory.
For each file, show whether it contains placeholder text (look for `{{`).
Files with no placeholders remaining = COMPLETE; files with placeholders = NEEDS_FILL.

---

## Update templates (action 4)

Load `./assets/module.yaml` for the current plugin version.
Read the version from `{project-root}/_bmad/config.yaml` (samd.module_version).
If versions match, report "already up to date."
If newer: list files that have changed in the new version.
Ask: "Update changed templates? Customized files (those without any remaining {{ tokens) will NOT be overwritten."
On confirm: run `scaffold-qms.py` with `--skip-customized` flag.
