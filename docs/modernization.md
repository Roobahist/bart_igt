# Modernization assessment and verification

Baseline: `1955f96` (the repository's single initial commit). The initial checkout
was clean, with five Python files, bundled media/fonts, three tracked bytecode
files and historical Excel output. No README, manifest, tests, CI, container or
agent instructions existed in the repository. No GitHub issues were returned.

## Verified findings and changes

| Finding | Priority | Resolution |
|---|---|---|
| `main.py` raises IndentationError at line 855 | Critical | Restored runnable orchestration; compile checks cover both launchers |
| Removed pandas `DataFrame.append` used for every response | High | Replaced direct pandas use with journaled records and openpyxl export |
| Broad catch around tasks reruns both after an execution error | High | Convert code separately; execute ordered tasks once; propagate failures |
| Only shutdown saves data; failed window creation can mask original error | High | Per-response durable journal and independent cleanup/export |
| Subject code becomes an unsanitized output path | High | Timestamp/UUID filenames, metadata remains in workbook |
| Excel can interpret participant strings as formulas | High | Force string cells to literal text |
| `images/Bart` differs from tracked `images/BART` | High | Corrected case and added asset preflight |
| Interrupted balloon credits uncollected reward | High | Bank only when collected; test skip after pumping |
| Pending Enter can also collect a bursting balloon | High | Guard terminal outcomes; one completed record per balloon |
| BART drops RT despite existing RT column | Medium | Monotonic elapsed time on completed BART trials |
| Two divergent 900-line launchers and repeated IGT branches | Medium | One compatibility launcher; shared deck replenishment logic |
| Survey uses `eval` to find known stimuli/configuration | Medium | Explicit stimulus lists and `getattr` for trusted settings |
| Privileged global keyboard polling and synchronous audio package | Medium | Native PsychoPy Keyboard state and preloaded Sound playback |
| Missing setup, tooling, regression protection and project guidance | Medium | Dependency files, Ruff, unittest, CI, Dependabot, README and AGENTS |

## Compatibility and deliberate limits

Persian survey labels, media, task order rules, default settings and workbook
columns/layout remain. Invalid task inputs now raise ValueError instead of returning
strings or failing inside random calculations. IGT decks reset for a new session.
Results use new filenames and an additional journal. `main (2).py` now follows the
canonical 1200×675 window and current video controls rather than its old 800×450
variant. Sound feedback is asynchronous and polling yields briefly. RT values are
monotonic elapsed trial time; these changes require manual study validation.

Existing historical output is preserved, including its Git tracking. Its sensitivity
has not been determined; any cleanup/history rewrite requires a separate human
decision. New output is ignored. Font/media licensing is not established by this
repository. No credentials, remote integrations or production resources were found
in the source reviewed.

Presentation remains procedural with single-session globals. Replacing every
stimulus declaration with a generalized UI framework would add regression risk
without a clear benefit. No Docker, CD, dependency injection framework, monitoring
service, CodeQL matrix or broad type-checking framework was added. Existing Python
logging handles operator stop and cleanup failures, while task errors propagate.

## Tools and verification

Ponytail repository audit identified duplicated launchers, repeated deck logic,
manual survey dispatch and unnecessary direct keyboard/audio/pandas dependencies.
Its final simplicity pass retained the existing presentation and removed duplicate
implementations; no additional architectural layers were justified. Correctness
and security were reviewed separately because Ponytail scopes those out.

Archify, Superpowers and Context7 were not installed or available as callable tools.
Their repositories were inspected; no third-party install scripts were run.
The editable architecture overview is Mermaid, not an Archify-generated artifact.
The official PsychoPy 2026.2.4 wheel/source and metadata were inspected to verify
native VLC and keyboard APIs and Python support. References:
[installation](https://psychopy.org/download),
[keyboard](https://psychopy.org/api/hardware/keyboard.html),
[audio](https://psychopy.org/api/sound/playback.html),
[package metadata](https://pypi.org/project/psychopy/2026.2.4/).

Baseline: three characterization tests passed; `main.py` failed compilation.
Final headless suite: 25 tests passed on Python 3.14.7 and Python 3.12.14, including task distribution,
input transitions, safe skip/burst/collect, task failure without rerun, dialog
cancel, failed window creation, failed export, formula safety, journal recovery
and asset resolution. Ruff lint/format checks and compilation passed. CI targets
Python 3.11; local headless tests do not install or run the PsychoPy desktop stack.

Pinned PsychoPy/openpyxl/et-xmlfile advisory audit reported no known vulnerabilities.
The full PsychoPy transitive/platform environment was not resolved or audited here.
CI audits only the complete pinned result-storage closure; full environment audit
remains a workstation task. GitHub-hosted CI results are separate from local checks.

PsychoPy is absent from the local Python 3.14 environment (outside its supported
runtime range); real GUI/video/audio startup and hardware timing have not been
executed. Follow `workstation-checks.md` before research use. No deployment or
merge is performed by this modernization.
