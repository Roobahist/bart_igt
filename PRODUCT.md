# Product

<!-- impeccable:product-schema 1 -->

## Platform and users

Primary: local browser experiment, HTML/CSS/JavaScript with vendored jsPsych.
Optional reference: Python/PsychoPy desktop. Participants complete SAM ratings,
watch a video and make decisions in IGT and BART. Operators configure the study
and download local results. No remote service or installation is required.

## Product truth

Preserve configured distributions, burst hazard, deck mapping, counterbalancing,
rewards, original instructions, SAM images and ordinal mappings, and canonical
result columns. Record intentional platform/timing/input differences rather than
claiming experimental equivalence. See `docs/browser-experiment.md`.

## Confirmed design requirements

The owner requested an entire browser redesign with a polished game interface,
not small revisions. They rejected antique serif/paper-tabletop treatments and
black revealed card faces. All decks must look equivalent. BART must have no line,
frame, floor shadow, scale or gauge that suggests a size limit or collection point.
Pump and Collect have equal visual emphasis. English and Persian are injected.

## Operating constraints

The owner does not want PsychoPy or new experiment software installed locally.
Use existing/bundled tooling for local tests and disposable runners for CI.
Keep participant data local, retain completed responses on interruption and provide
recovery downloads. Do not commit participant data or deploy without authorization.
Screenshots use labeled synthetic input; timing and behavioral validity need manual
workstation checks before collection.
