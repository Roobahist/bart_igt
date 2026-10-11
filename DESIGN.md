# Task design

The owner chose a modern, polished game interface. Apply Impeccable's Operate,
distill and typography guidance to the existing task objects, preserving content
and study behavior. The skill source was read at commit
`c63b8dd7dd5a5f3c32eaabe1af76d0694f863ed2`; its CLI/detectors were not installed
or run, and no web detector result is claimed for this native Python application.

- One sans family per language. English uses bundled Regular/Bold Plus Jakarta
  Sans, registered inside the process; Persian retains its existing IRANSans face.
  No serif display role, decorative numbering or font installation.
- Cool light canvas, white revealed faces, saturated blue matching deck backs and
  a coral balloon. Accent belongs to task objects and feedback, not unrelated UI.
- Actual four-card choices retain a shallow stack and equal hit areas. A compact
  geometric card mark replaces the engraved diamond frames. Press state changes
  the inner edge without moving the target. Feedback stays inside the selected card.
- The balloon grows on an open, uninterrupted field. No horizontal rule, framing
  band, measuring graphic, floor or fixed shadow is drawn around its growth area.
  Status and key legends stay to the side. The window edge is the only viewport
  boundary; there is no decoration suggesting a burst threshold.
- Keep written instructions, trial controls, task distributions and feedback hold
  unchanged. No entrance animation or added delay in a timed experiment.
- Verify once in a batched real-render pass, fix findings together, and confirm
  once. Include zero, twenty and 127-pump BART frames, choice/reveal cards and both
  desktop layout directions. Headless tests cannot establish behavioral neutrality.

See `docs/ui-design.md` for protocol implications and capture limits.
