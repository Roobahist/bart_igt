# Working on BART / IGT

Primary interface: bilingual browser research experiment in `apps/browser/`, using a
vendored jsPsych runtime and no build or remote service. `apps/browser/study-model.js` holds the
scientific rules, `apps/browser/experiment.js` orchestrates session screens and recoverable browser
results, and `apps/browser/styles.css` owns presentation. `study/settings.py` remains the scientific
source of truth; run `scripts/export_study_settings.py` after changes. Inject locale
catalogs from `study/locales/` and `apps/browser/locales/`; use canonical stored values.

The optional PsychoPy reference remains in `apps/desktop/experiment.py`, `apps/desktop/presentation.py`, `study/tasks/balloon.py`, `study/tasks/cards.py`,
`apps/desktop/results.py` and `apps/desktop/localization.py`. See `docs/browser-experiment.md` for intentional
platform and protocol differences and `DESIGN.md` for browser presentation.

- Preserve column names/order configuration, sparse metadata-first workbook layout,
  task counterbalancing, loss block distributions and burst probabilities.
- Do not introduce BART lines, frames, floor shadows, scales or gauges that imply
  a balloon size limit or recommend a collection threshold. Keep status to the side.
- Do not change scientific defaults, instructions or timing without documenting the
  effect and requiring manual workstation validation before data collection.
- Keep participant-facing text/fonts/script settings in locale catalogs and inject
  the same catalog through `run(catalog=...)` into every screen. Preserve template
  keys/parameters across locales and canonical result values. Controls live in config.
- Keep PsychoPy imports inside `run()` so headless tests can import the modules.
- Prefer small functions and browser/native standard features over new dependencies.
  Do not introduce remote runtime assets or CDN requirements.
- Desktop responses use `SessionResults`; retain crash journals. Browser responses
  must save after each completed response, stop on write failure and offer local
  journal/CSV downloads. Retain prior sessions and label synthetic capture fixtures.
  Never interpolate participant input into file paths or Excel formulas.
- Never commit new participant data, logs, credentials, caches or virtualenvs.
  Do not delete historical workbooks or rewrite history to remove them autonomously.
- No production deployment, remote services or required environment variables.

Install `requirements/development.txt`, then run `ruff check .`, `ruff format --check .`,
`python -m unittest discover -s tests/desktop -v`, and
`python -m compileall -q apps/desktop study scripts`.
Audit pinned storage dependencies with
`pip-audit --strict --no-deps --disable-pip -r requirements/results.txt`.
Desktop compatibility and timing require the checklist in `docs/workstation-checks.md`.

If giving the user directly reusable content with placeholders, put a bold notice
at the top that the placeholders need correct values before use.

Desktop English screenshots in `docs/screenshots/desktop/` are genuine PsychoPy frames captured
remotely with scripted demonstration input. Use the hosted **Desktop English screenshots**
workflow to regenerate them; never install PsychoPy on the owner's machine without
explicit authorization. Keep provenance and limits with the images; do not present
scripted captures as physical timing, audio/video or participant-session validation.

Browser checks: `node --test tests/browser/study-model.test.js`, configuration exporter
`--check`, and Playwright integration in `tests/browser/experiment.test.cjs`. Browser screenshot
CI installs test tooling only on disposable runners. Local tests use existing
Chrome and bundled tooling; do not install browsers or experiment dependencies
without explicit authorization. Do not claim physical timing validation.
