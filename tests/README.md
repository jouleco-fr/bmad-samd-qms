# Tests

End-to-end tests of the plugin: each one builds a throw-away project, runs the plugin's own
scripts with the answers in `fixtures/answers.json`, and checks the result.

| Test | What it checks |
|---|---|
| `test_scaffold_creates_every_document_from_the_answers` | every template becomes a document under `qms/`, with no placeholder left |
| `test_a_rerun_never_overwrites_an_edited_document` | a document someone has edited survives a second run |
| `test_setup_registers_the_module_with_the_answers` | the `samd` module and its answers reach `_bmad/config.yaml` |
| `test_every_wired_workflow_gets_its_own_file` | one `_bmad/custom/<skill>.toml` per workflow in `assets/wiring.toml` |
| `test_a_second_wiring_changes_nothing` | re-running the wiring is harmless |
| `test_the_wiring_never_overwrites_a_teams_own_file` | a team's own customisation file is refused, reported, and left intact |
| `test_bmads_own_resolver_loads_the_qms_into_every_wired_workflow` | BMAD's own resolver returns the QMS documents for every wired workflow, and each of them exists |

The last test is the one that matters most: it checks what BMAD will actually load, which is
how a wiring that never worked went unnoticed for ten weeks in 2026. It needs a BMAD
installation; without one it is skipped, and the run says so.

## Run

```bash
BMAD_PROJECT=/path/to/a/project/with/bmad python3 -m unittest discover -s tests -v
```

Requires Python 3.11 or later, and `pyyaml` for `merge-config.py`.

## Results

| Date | Plugin commit | BMAD | Python | Result |
|---|---|---|---|---|
| 2026-11-02 | the commit that added these tests | 6.10.0 | 3.12.3 | 7 tests, all passed |
