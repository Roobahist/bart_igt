# Path migration

This organization replaces the mixed root-level desktop files and scattered media
with explicit application, study, asset, test and archive boundaries. File moves
change imports and paths, not task algorithms, distributions, controls or content.

| Previous path | Current path or command |
| --- | --- |
| `web/` | `apps/browser/` |
| `web/app.js` | `apps/browser/experiment.js` |
| `web/model.js` | `apps/browser/study-model.js` |
| `web/server.js` | `scripts/serve-browser.mjs` |
| `web/study-config.json` | `study/browser-settings.json` |
| `config.py` | `study/settings.py` |
| `locales/` | `study/locales/` |
| `main.py` | `python -m apps.desktop.experiment` |
| `ui.py` | `apps/desktop/presentation.py` |
| `session.py` | `python -m apps.desktop.results` |
| `localization.py` | `apps/desktop/localization.py` |
| `bart.py`, `igt.py` | `study/tasks/balloon.py`, `study/tasks/cards.py` |
| `images/`, `fonts/`, `videos/`, `sounds/` | `assets/` with lowercase folder names |
| `requirements*.txt` | `requirements/desktop.txt`, `results.txt`, `development.txt` |
| `scripts/export_browser_config.py` | `scripts/export_study_settings.py` |
| `scripts/capture_screenshots.py` | `scripts/capture_desktop_screenshots.py` |
| Root Python tests and `web/tests/` | `tests/desktop/` and `tests/browser/` |
| Native frames at `docs/screenshots/` | `docs/screenshots/desktop/` |
| Old workbooks in `output/` | `archive/results/`, original names and bytes retained |
| `videos/hardsub.rar` | `archive/media/hard-subtitles.rar` |

New desktop sessions write to ignored `results/`, not the historical archive.
No historical workbook, source media or font was deleted; media/archive file hashes
were checked before and after the moves. Older desktop capture provenance keeps
its original source commit and paths, which refer to that historical commit.
Browser captures and their source hashes are regenerated for the current layout.

The old `/web/` preview URL redirects through the Node launcher. With Python's
static server, use `/apps/browser/` directly. Existing local storage remains tied
to the original origin and profile, not the page path; previous session downloads
remain available without converting or renaming participant records.
