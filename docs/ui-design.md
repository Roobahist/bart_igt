# Task presentation decisions

## Direction: a quiet tabletop

The native task interface uses warm paper, blue-grey printed card backs, serif
headings and a clay-colored vector balloon. This brings physical task objects
into focus. It avoids dashboard tiles, oversized choice numerals, casino effects,
risk gauges and decoration that recommends a strategy. The written instruction
layouts retain their previous hierarchy and content.

The UI/UX Pro Max skill's tactile/skeuomorphic guidance informed the material
metaphor and depth. Its generic marketing page and dark casino palette were not
applied to this research application. All shapes are native PsychoPy geometry;
no generated illustration, extra renderer or image dependency is required.

## Iowa Gambling Task

- Each deck has the same printed diamond pattern, border and layered paper edges.
  A label below identifies its original deck number. No deck is visually ranked.
- A press brightens the inner printed border without moving its hit region.
  Release reveals a warm light card, with corner numerals and separated gain/loss
  lines. Labels and signed amounts carry meaning independently of color.
- The header groups the task name and prompt on one side and the balance on the
  other. The footer reports choice progress. Balance updates after the configured
  feedback hold, as before. No net badge or deck history is introduced.
- The original solid-black front image and ornate back assets remain historical
  media in the repository; the running task no longer requires them.

## Balloon task

- A purpose-drawn balloon, curved reflection, knot, string and ground shadow replace
  the glossy red raster image and separate rope image. The object sits on the left
  of an open stage; the current reward and collected bank form a ledger on the right.
  This composition mirrors for Persian. The title/progress and keyboard legends
  occupy separate rows, outside the balloon's growth region.
- The balloon grows continuously with successful pumps between configurable
  viewport-relative minimum and maximum sizes. Both the start and near-maximum
  states are captured, in addition to the twenty-pump demonstration.
- The keyboard legends describe the existing pump/collect keys. They are not
  clickable buttons. No pressure gauge, burst prediction, countdown or pump
  recommendation is added. Audio and action rules retain their existing settings.

SAM figures, rating order and response rules remain unchanged. Instructions retain
all their original catalog content. Body fonts and optional `display_font` come
from the injected locale; `config.ui_theme` supplies colors and
`config.bart_presentation` supplies balloon dimensions. Shapes and layout scale
with the viewport. No fonts or experiment dependencies were installed locally.

## Scientific scope and verification

The loss distributions, gains, deck mapping, counterbalancing, balances, response
logging, mouse press/release rules, burst hazard and configured feedback duration
are unchanged. Balloon artwork, initial size, location and visual growth range
have changed substantially. Card styling and explicit zero-loss feedback also
change presentation. Review these against the study protocol before collecting
or comparing data; do not assume equivalence with earlier sessions.

Headless regression tests cover task outcomes and geometric separation at several
desktop sizes. Real English OpenGL captures come from the hosted workflow using
scripted input. A seed of 219 permits a separate real-rule BART demonstration to
reach 127 successful pumps; bursts are not disabled or overridden. These are
synthetic demonstrations, not human sessions. They cannot validate physical
input/timing, font shaping or audio/video on the intended workstation. Follow
[the workstation checklist](workstation-checks.md) in both languages before data
collection.
