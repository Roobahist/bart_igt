"""Guard task artwork against overlaps at supported desktop viewport sizes."""

from types import SimpleNamespace
import unittest

from study import settings as config
from apps.desktop.localization import load_catalog
from test_experiment import Stimulus
from apps.desktop.presentation import BartScreen


class TaskLayoutTests(unittest.TestCase):
    def test_balloon_and_knot_stay_in_viewport_and_away_from_status_text(self):
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
                        self.assertLess(y + height / 2, size[1] / 2)
                        self.assertGreater(y - height * 0.59, -size[1] / 2)
                        self.assertLess(abs(x) + width / 2, size[0] / 2)
                        self.assertLess(width / 2, abs(screen.value.pos[0] - x) - size[0] * 0.125)

    def test_no_thin_horizontal_rectangles_are_drawn_across_the_balloon_field(self):
        drawn = []

        class Rectangle(Stimulus):
            def draw(self):
                drawn.append(self)

        screen = BartScreen(
            SimpleNamespace(TextStim=Stimulus, Rect=Rectangle, ShapeStim=Stimulus),
            SimpleNamespace(size=(1200, 675)),
            load_catalog("en"),
            config.ui_theme,
            config.controls,
            config.bart_presentation,
        )
        screen.draw(1, 5, 0, 0, 0, 128)
        self.assertFalse(
            any(stimulus.width > 480 and stimulus.height < 10 for stimulus in drawn),
            "A horizontal divider can imply a burst/collect threshold",
        )
