# Workstation checks before data collection

These checks require the actual participant workstation and are not automated CI.

1. Install PsychoPy 2026.2.4 and same-architecture VLC; verify desktop graphics,
   keyboard backend, audio backend, MP3 decoding and installed IRANSans fonts.
   Confirm Persian shaping and English LTR rendering, endpoint labels and all survey numbers at the intended
   resolution/fullscreen setting. Review media redistribution rights separately.
2. Run `main.py` from PsychoPy Coder and from a different working directory.
   Cancel the participant dialog: no new output should appear.
3. Use a test subject with an even code and then an odd code. Confirm task ordering,
   two required survey ratings, configured trial counts and correct metadata.
4. For each video choice test play, pause/resume (`p`), replay (`r`) and skip (`i`).
5. Click IGT cards once per press/release; verify feedback, bank totals, trial counts
   and recorded choices/gains/losses. Test the task skip key.
6. Hold Space in BART with the default setting: one pump per press. Release and
   press again; test banking on Enter release and zero gain after a burst. Skip a
   partly inflated balloon: uncollected reward must not appear in the bank.
7. Test Escape during surveys, each task and video. Confirm window/video cleanup,
   journals and workbooks. Inspect BART RT and IGT RT on the actual hardware.
8. Recover a test journal and compare its records with the original workbook.
   Review available disk space and access permissions. Never use real participant
   data for fault injection or CI.
9. Verify keyboard polling, rendering/frame timing and asynchronous audio feedback
   satisfy the approved study protocol. Finite held-key repeat settings are based
   on poll counts, not milliseconds, and need separate calibration.
10. Record PsychoPy/Python/VLC versions and run `python -m pip check` plus a full
    installed-environment vulnerability audit before deploying this workstation.

No hardware timing precision or desktop compatibility is inferred from mocked tests.

Run the survey/task checks with both `language = "fa"` and `language = "en"`.
Confirm English uses Latin rating buttons, Persian keeps its original digit images,
and stored categorical/ordinal values remain the same. Check configured keys match
instruction text. Videos are shared assets; embedded speech/subtitles do not change
with the interface language. Review English wording against the approved protocol.
