---
name: qms-update
description: Update SaMD QMS templates to a newer version of the bmad-samd-qms plugin, preserving files you have customized. Alias for /qms-init update.
---

# SaMD QMS Update

This skill is an alias for `/qms-init update`. It delegates immediately to qms-init's update action.

## On Activation

Load `../qms-init/SKILL.md` and execute the **Update templates (action 4)** section.

The update logic:
1. Reads the plugin version from `./assets/module.yaml` (samd section, `module_version`)
2. Compares against the installed version in `{project-root}/_bmad/config.yaml`
3. Lists files that differ between the installed version and the current plugin templates
4. Skips files that have been customized (no `{{` tokens remaining) unless `--force` is passed
5. Applies updates to remaining files
6. Reports what was updated / skipped
