# Browser screenshots

Genuine frames from the redesigned browser experiment using jsPsych 8.3.0,
scripted synthetic input and English/Persian catalogs. Captures were made locally
in the already-installed Chrome using an isolated temporary profile; no PsychoPy,
VLC, fonts, browser or experiment dependencies were installed on the machine.

These demonstrate the actual running UI. They do not validate physical timing,
complete participant sessions, audio perception or scientific equivalence.
The full [provenance](provenance.json) records the browser, viewport, RNG fixtures
and tested behavior. No participant data is included. The 20/127-pump growth
captures use an explicit no-burst RNG fixture to inspect layout; a separate trial
tests an explosion. These are not natural sampled behavioral results.

## English desktop

![Session setup](english-setup.png)
![SAM ratings](english-survey.png)
![IGT instructions](english-igt-instructions.png)
![IGT deck selection](english-igt-choice.png)
![Light card reveal](english-igt-reveal.png)
![BART initial balloon](english-bart-start.png)
![BART at twenty pumps](english-bart-pumped.png)
![BART at 127 pumps](english-bart-large.png)
![Completion and downloads](english-completion.png)

## Phone and Persian

![English BART phone layout](english-bart-mobile.png)
![Persian setup](persian-setup-mobile.png)
![Persian SAM](persian-survey-mobile.png)
![Persian BART](persian-bart-mobile.png)
![Persian card choice](persian-igt-mobile.png)
![Persian card reveal](persian-igt-reveal-mobile.png)

## Reproduce

`web/tests/browser.cjs` uses Playwright with the locally served repository.
The **Browser checks** workflow installs test tooling on an ephemeral runner,
tests the actual flow and uploads captures. Source code does not require those
test dependencies to run. Provenance travels with regenerated images; desktop
and browser screenshots are labeled separately.
