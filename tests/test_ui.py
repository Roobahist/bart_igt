"""Guard task artwork against overlaps at supported desktop viewport sizes."""

from types import SimpleNamespace
import unittest

import config
from localization import load_catalog
from test_experiment import Stimulus
from ui import BartScreen


class TaskLayoutTests(unittest.TestCase):
    def test_balloon_and_knot_stay_between_header_and_controls_and_away_from_ledger(self):
        for size in ((1200, 675), (1024, 768), (1600, 900)):
            for language in ("en", "fa"):
                screen = BartScreen(
                    SimpleNamespace(TextStim=Stimulus, Rect=Stimulus, ShapeStim=Stimulus),
                    SimpleNamespace(size=size),
                    load_catalog(language),
                    config.ui_theme,
                    config.controls,
                    config.bart_presentation,
                )
                for pumps in (0, 20, 127):
                    with self.subTest(size=size, language=language, pumps=pumps):
                        screen.draw(1, 5, pumps * config.bart_blow_addition, 0, pumps, 128)
                        x, y = screen.balloon.pos
                        width, height = screen.balloon.size
                        self.assertLess(y + height / 2, screen.rule.pos[1])
                        self.assertGreater(
                            y - height * 0.59, screen.legends[0].pos[1] + size[1] * 0.04
                        )
                        self.assertLess(abs(x) + width / 2, size[0] / 2)
                        self.assertLess(width / 2, abs(screen.value.pos[0] - x) - size[0] * 0.125)
