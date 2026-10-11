# Architecture and naming

The repository separates executable applications, scientific configuration, media,
verification and historical artifacts. Browser and desktop launch independently;
no loose application modules or media directories live at the repository root.

| Location | Responsibility |
| --- | --- |
| `apps/browser/index.html` | Primary browser entry point |
| `apps/browser/experiment.js` | Session timeline, screens, input and local recovery |
| `apps/browser/study-model.js` | Pure browser task rules, formatting and exports |
| `apps/browser/styles.css` | Browser presentation |
| `apps/browser/locales/` | Browser-specific interface copy |
| `apps/browser/vendor/` | Pinned jsPsych runtime and upstream license |
| `apps/desktop/experiment.py` | Optional native session orchestration |
| `apps/desktop/presentation.py` | Native task rendering |
| `apps/desktop/localization.py` | Injected catalogs and process-local font registration |
| `apps/desktop/results.py` | Durable journals, compatible workbook export and recovery |
| `study/settings.py` | Study settings, controls and asset paths |
| `study/browser-settings.json` | Generated browser settings; CI checks drift |
| `study/locales/` | Shared original instructions and rendering metadata |
| `study/tasks/` | Python balloon hazard and card loss-block rules |
| `assets/` | Shared unchanged images, fonts, videos and sounds |
| `scripts/` | Serving, settings export and desktop capture tools |
| `tests/browser/`, `tests/desktop/` | Platform-specific verification |
| `docs/screenshots/browser/`, `docs/screenshots/desktop/` | Separate actual-render galleries |
| `requirements/` | Desktop, results-only and development dependency sets |
| `archive/` | Historical workbooks and unused source media |

Python modules use descriptive snake_case names. JavaScript modules and media
folders use descriptive kebab-case names. `index.html`, `styles.css`, `README.md`
and package manifests keep conventional names. Sequential SAM/numeral assets keep
numeric filenames within descriptive folders. Font-internal family names and
third-party jsPsych bytes are preserved. Historical result filenames are retained
for provenance rather than made to look like current application output.

## Dependency flow

`study/settings.py` → `scripts/export_study_settings.py` →
`study/browser-settings.json` → browser session and pure model.

The desktop imports the same study settings and catalogs plus Python task rules.
PsychoPy imports remain lazy inside `run()`; headless checks require no display or
native experiment installation. Browser usage requires no Python packages.

Both platforms preserve canonical result fields, counterbalancing, configured
loss distributions and balloon hazard. The browser retains completed responses in
local storage; the desktop flushes a JSONL journal and atomically writes Excel.
Browser journals remain compatible with desktop workbook recovery.

Repository-relative assets resolve from the package's repository root on desktop
and the browser document URL online. The local Node server redirects `/` and the
former `/web/` URL to `/apps/browser/`; no duplicate old implementation is retained.
Browser storage keys and origin remain unchanged, preserving existing recovery
records when the same local server port and browser profile are used.

See [browser protocol differences](browser-experiment.md),
[desktop instructions](desktop-experiment.md), and
[the path migration guide](project-structure.md).
