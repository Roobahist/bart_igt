# Browser experiment

The primary interface is now a build-free browser application in `web/`, using
vendored jsPsych 8.3.0 for the session timeline and custom screens for the study.
PsychoPy remains an optional desktop reference implementation. Neither PsychoPy,
VLC, Node packages nor OS fonts are needed to use the browser experiment.

## Run locally

From the repository root, use Python's existing static file server:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/web/ in a current desktop browser. If Node is already
available, `node web/server.js` provides an alternative local server with media
range requests. Do not open `index.html` as a file: JSON catalogs require HTTP.
Keep the server local. No hosted services, account, credentials or deployment are
required. All page resources are served from this repository. The original
videos, SAM images and sounds are reused; no media or experiment software is
installed on the operating system.

English is the browser presentation default. Choose Persian before starting, or
open `web/?lang=fa`. The selected language cannot change during a session.
Catalogs are injected into every screen. Canonical categories and result columns
are unchanged across languages. Persian uses the existing bundled font files.
Check the existing media and font redistribution rights before publishing.

## Configuration

`config.py` remains the scientific source of truth. After editing it, regenerate:

```sh
python3 scripts/export_browser_config.py
```

The generated `web/study-config.json` contains configured controls, video, trial
counts, SAM paths, gains, loss blocks, capacity, reward and timing. Browser colors,
layout and motion tokens are in `web/styles.css`. Participant-facing browser copy
is in `web/locales/`; original instructions come from the existing `locales/`.
`web/instruction-layouts.json` groups their lines into localized sections without
rewriting or duplicating the original wording; tests verify exact text coverage.
CI rejects configuration drift. Browser default language is intentionally English.
No distributions, capacities or recommended thresholds appear on task screens.

The browser requires a fresh keypress per pump. It does not support the desktop
`bart_blowing_factor` repeat-pumping option; the exporter rejects nondefault
repeat-pumping settings instead of silently substituting behavior.

## Scientific compatibility and deliberate differences

- Sequence: fixation → SAM → video → SAM → counterbalanced tasks → payout.
  Odd integer participant codes put BART first; other codes put IGT first.
- IGT: same four deck mappings, gains and independently shuffled complete loss
  blocks, replenished without dropping losses. Browser Fisher–Yates and Python
  sampling have the same distributions; identical seeds do not produce identical
  trial sequences across languages. New sessions reset every deck.
- BART: conditional hazard `1 / (capacity + 1 - pumps)`, guaranteed burst at
  capacity, same reward and zero reward for exploded or skipped balloons. Completed
  collections remain credited when a later balloon is skipped. No risk gauge,
  capacity mark, floor shadow or balloon frame is drawn. The knot, neck and rope
  stay fixed while the upper body expands upward; attachment paths are tested at
  zero, twenty and 127 pumps. This is a presentation change, not a probability change.
- IGT clicks are recorded on activation/release. BART keyboard pumping occurs on
  fresh keydown; keyboard collection and instruction advancement occur on keyup.
  Held keys and key-repeat cannot carry a pump into the next trial. Pointer and
  accessible keyboard activation are additional input modes, recorded separately.
- Response clocks use `performance.now()` after a `requestAnimationFrame` callback.
  RT is seconds. This is a browser-render estimate, not verified physical stimulus
  onset or hardware timing. IGT uses the configured two-second feedback hold; its
  card turn runs within that hold. Balloon growth updates immediately, with no
  extra animation wait or new burst/collection hold.
- Video needs an explicit Play action because browsers restrict autoplay. It can
  be paused/replayed/skipped using configured operator keys. This changes the
  transition into the video and must be recorded in the protocol.
- Lost focus / hidden tabs stop accepting input and pause video. Resume requires
  an explicit action; interruption duration is logged. Trial RT includes the
  interruption. Review affected trials before analysis. Feedback can be extended
  while a window is inactive. Screen geometry, input modalities, colors, SAM layout
  and typography are new stimuli; do not pool versions without study review.
- SAM retains the original five stimulus images and 1–9 ordinal values. Image and
  numeric value order stay fixed left to right, including in Persian, matching the
  original mapping rather than accidentally reversing it with the RTL layout.

Before participant use, verify workstation timing, complete-duration video/audio,
SAM endpoints, configured controls, payouts, interruption policy, browser storage
and actual input devices against the study protocol. Automated tests and scripted
captures do not establish behavioral neutrality or experimental equivalence.

## Results and recovery

Completed responses are synchronously stored in browser local storage. Every
session has a UUID key. A failed write stops the session and offers downloads of
in-memory rows; it never silently proceeds. A reload shows prior sessions with
recovery downloads, including incomplete sessions. It does not resume unfinished
trials or reconstruct randomness. New sessions retain old sessions.

Download CSV, a compatible JSONL journal, and a detailed JSON session record.
CSV keeps the original column order and sparse metadata-first rows; strings that
could become spreadsheet formulas are prefixed with an apostrophe. JSONL preserves
exact canonical values and can use the existing optional Excel recovery tool:

Run `session.py` with the downloaded journal path as its sole argument, using the
existing optional results dependencies. Browser use itself requires no Python packages. JSON session details
include the configuration, language, environment, input modes and interruptions;
additional audit events do not alter canonical CSV/XLSX columns.

Browser storage belongs to this browser profile and origin. Private browsing,
clearing browser data, quota limits or changing the server port can make saved
sessions unavailable. Storage is not encrypted and is not a filesystem crash
journal. Download after each session and follow your participant-data policy.
No results are uploaded anywhere. No real participant data is committed.

## Verification

`node --test web/tests/model.test.js` checks distributions, burst boundaries,
ordering, export safety, configuration and locale parity. `web/tests/browser.cjs`
uses Playwright for complete scripted sessions, actual video playback/pause/replay,
RTL/mobile rendering, key repeat, recovery, abort and failed-storage behavior.
Playwright and its browser are installed only on disposable CI runners; locally,
verification used bundled tooling and the existing Chrome with a temporary profile.
See [browser screenshots and provenance](screenshots/browser/README.md).
