# Working on BART / IGT

This is a Persian PsychoPy desktop research experiment, not a web application.
`main.py` orchestrates SAM → video → SAM → counterbalanced IGT/BART → payout screen.
`igt.py` and `bart.py` preserve study randomization; `session.py` owns local result
storage and configuration validation. Assets and study settings live in the
existing directories and `config.py`. `main (2).py` is only a compatibility launcher.

- Preserve column names/order configuration, sparse metadata-first workbook layout,
  task counterbalancing, loss block distributions and burst probabilities.
- Do not change scientific defaults, instructions or timing without documenting the
  effect and requiring manual workstation validation before data collection.
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
`python -m compileall -q main.py 'main (2).py' bart.py igt.py config.py session.py`.
Audit pinned storage dependencies with
`pip-audit --strict --no-deps --disable-pip -r requirements-results.txt`.
Desktop compatibility and timing require the checklist in `docs/workstation-checks.md`.

If giving the user directly reusable content with placeholders, put a bold notice
at the top that the placeholders need correct values before use.
