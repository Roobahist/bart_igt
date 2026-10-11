# Task presentation decisions

The original IGT front image (`images/IGT/front1.png`) contains a solid black
face. It did not convey an outcome; gains and losses appeared in detached,
brightly colored bars above the decks. The new renderer replaces those assets
with native PsychoPy rectangles and text.

- All four unselected decks have the same pale surface, size and styling. The
  number and deck label identify a choice; appearance does not rank the decks.
- On release, the chosen card gets a white face and a blue outline. Gain and loss
  appear on that card, with explicit labels, signs and two decimal places.
  Both are shown, including a zero loss, so an empty space cannot be mistaken
  for missing feedback. Color reinforces the labels rather than replacing them.
- The header holds the task name and balance. A separate footer shows the current
  choice and configured total. No net-result badge, deck history, recommendation
  or burst probability is added.
- Task instructions keep their existing content, with a heading and constrained
  reading width. BART's existing value, trial and bank text move to the header;
  the balloon's position, size and growth mapping remain unchanged.
- SAM figures, rating order and selection rules stay unchanged. These are study
  stimuli, rather than decoration to redraw casually.

`ui.py` accepts a locale catalog and theme from the caller. Participant-facing
copy is in `locales/en.json` and `locales/fa.json`; colors are in `config.ui_theme`.
No new fonts, animation framework or runtime dependencies are required. The
original IGT images remain in the repository as historical assets, but are no
longer configured or required by the task.

## Scientific scope and verification

The loss distributions, gains, choice mapping, balance calculation, response
logging, mouse press/release behavior and configured feedback duration are
unchanged. Balance still updates after the feedback hold. Layout and the explicit
zero-loss display are presentation changes and may affect attention or behavior:
review them against the study protocol before collecting or comparing data.
Do not assume equivalence with sessions collected using the previous layout.

Headless outcome tests cover all decks, an outside click, zero loss and a negative
net result. Real English OpenGL screenshots are generated remotely through the
hosted capture workflow. That demonstration cannot validate physical timing,
mouse accuracy, Persian font shaping or audio/video on a participant workstation.
Check both languages, click targets and feedback at the intended resolution using
[the workstation checklist](workstation-checks.md) before data collection.
