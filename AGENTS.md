# Working on BART / IGT

This is a Persian/English PsychoPy desktop research experiment, not a web application.
`main.py` orchestrates SAM → video → SAM → counterbalanced IGT/BART → payout screen.
`igt.py` and `bart.py` preserve study randomization; `session.py` owns local result
storage and configuration validation. `localization.py` loads JSON catalogs from `locales/`. Assets and study settings live in the
existing directories and `config.py`. `main.py` is the single application entry point.

- Preserve column names/order configuration, sparse metadata-first workbook layout,
  task counterbalancing, loss block distributions and burst probabilities.
- Do not change scientific defaults, instructions or timing without documenting the
  effect and requiring manual workstation validation before data collection.
- Keep participant-facing text/fonts/script settings in locale catalogs and inject
  the same catalog through `run(catalog=...)` into every screen. Preserve template
  keys/parameters across locales and canonical result values. Controls live in config.
- Keep PsychoPy imports inside `run()` so headless tests can import the modules.
- Prefer small functions and native PsychoPy/standard-library features over new
  abstractions or dependencies. Presentation globals are single-session state.
- Append completed responses through `SessionResults`; retain crash journals.
  Never interpolate participant input into file paths or Excel formulas.
- Never commit new participant data, logs, credentials, caches or virtualenvs.
  Do not delete historical workbooks or rewrite history to remove them autonomously.
- No production deployment, remote services or required environment variables.

Install `requirements-dev.txt`, then run `ruff check .`, `ruff format --check .`,
`python -m unittest discover -s tests -v`, and
`python -m compileall -q main.py bart.py igt.py config.py session.py localization.py`.
Audit pinned storage dependencies with
`pip-audit --strict --no-deps --disable-pip -r requirements-results.txt`.
Desktop compatibility and timing require the checklist in `docs/workstation-checks.md`.

If giving the user directly reusable content with placeholders, put a bold notice
at the top that the placeholders need correct values before use.

English screenshots in `docs/screenshots/` are genuine PsychoPy frames captured
remotely with scripted demonstration input. Use the hosted **English screenshots**
workflow to regenerate them; never install PsychoPy on the owner's machine without
explicit authorization. Keep provenance and limits with the images; do not present
scripted captures as physical timing, audio/video or participant-session validation.
