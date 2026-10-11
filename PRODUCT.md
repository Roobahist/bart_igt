# Product

<!-- impeccable:product-schema 1 -->

## Platform

Desktop Python/PsychoPy. This is a native research experiment, not a web or phone app.
Impeccable's app guidance is adapted to this platform; no web CLI workflow is required.

## Users and purpose

Participants complete SAM ratings, watch a video and make repeated decisions in
IGT and BART. An operator configures the study and collects local result files.
The application records decisions and outcomes for research; it does not advise
participants which deck to choose or when to collect a balloon.

## Operating context

One local participant session at a time, with Persian or English presentation.
Actual workstation input, display timing, audio/video and font shaping require
manual verification. Repository screenshots are remote scripted demonstrations.

## Capabilities and constraints

Preserve randomization, burst hazard, deck mapping, task order, rewards, response
logging, controls, configured hold times, instructions and SAM stimulus images.
The owner does not want PsychoPy, dependencies or fonts installed on their machine;
render verification uses disposable GitHub runners. Font assets may be loaded by
an experiment process without OS installation. New participant data must not be
committed. A new PR merge requires the owner's instruction.

## Confirmed presentation requirements

The owner selected a polished game interface. They rejected antique serif type
and the paper/tabletop styling. Card stacks remain an acceptable mechanism, but
need a modern presentation. IGT outcomes belong on the selected card. BART must
not draw a line, frame, floor shadow, scale or gauge that implies a size limit or
suggests when to collect. Improved written instruction layouts should be retained.

## Evidence and principles

Current renderer: `ui.py`; settings: `config.py`; injected language: `localization.py`
and `locales/`; real captures and provenance: `docs/screenshots/`.
Readability and neutral task behavior take precedence over decoration. All decks
have equivalent styling. Presentation revisions are documented and must not be
assumed experimentally equivalent to prior sessions.
