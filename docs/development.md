# Development and verification

Run commands from the repository root. Browser use needs no package installation.
With an existing Node runtime, `npm start` or `node scripts/serve-browser.mjs`
starts the local server; `npm test` runs the pure browser model checks.

To use Python's existing static server instead:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/apps/browser/.

## Optional Python development environment

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/development.txt
ruff check .
ruff format --check .
python -m unittest discover -s tests/desktop -v
python -m compileall -q apps/desktop study scripts
python scripts/export_study_settings.py --check
pip-audit --strict --no-deps --disable-pip -r requirements/results.txt
```

On Windows, activate `.venv\Scripts\activate`. Native runtime installation is
separate in `requirements/desktop.txt`; results-only workbook recovery uses
`requirements/results.txt`. Headless tests do not import PsychoPy.

## Browser integration

`tests/browser/experiment.test.cjs` uses Playwright against the locally served
repository. CI installs pinned test tooling and a browser on disposable runners,
then checks real session flow, media loading, RTL, mobile layouts, export/recovery,
fixed balloon attachments and storage failure. Local verification uses the already
installed Chrome and bundled tooling, with an isolated temporary profile.
No PsychoPy or new experiment dependencies are installed on the owner's machine.

## Desktop screenshots

The read-only **Desktop English screenshots** workflow runs
`scripts/capture_desktop_screenshots.py` on an ephemeral PsychoPy/Xvfb runner.
Captures demonstrate rendering, not physical timing or participant behavior.
The optional native workstation checks remain in `workstation-checks.md`.
