import importlib
import unittest
from collections import Counter
from unittest.mock import patch

from study import settings as config
from study.tasks import balloon as bart
from study.tasks import cards as igt


class TaskCharacterization(unittest.TestCase):
    def setUp(self):
        importlib.reload(igt)

    def test_igt_preserves_each_configured_loss_block(self):
        for deck in range(1, 5):
            losses = getattr(config, f"igt_deck{deck}_all_losses")
            gain = getattr(config, f"igt_deck{deck}_gain")
            for _ in range(3):
                draws = [igt.gain_loss(deck) for _ in losses]
                self.assertEqual(Counter(loss for _, loss in draws), Counter(losses))
                self.assertTrue(all(g == gain for g, _ in draws))

    def test_bart_capacity_always_bursts(self):
        self.assertEqual(bart.burst_or_not(config.bart_max_balloon_capacity), 1)

    def test_bart_conditional_probability(self):
        with patch.object(bart.random, "choices", return_value=[0]) as choose:
            bart.burst_or_not(1)
            self.assertAlmostEqual(
                choose.call_args.kwargs["weights"][1], 1 / config.bart_max_balloon_capacity
            )


class TaskValidation(unittest.TestCase):
    def test_invalid_bart_inputs(self):
        for pump in (0, -1, 129, True, 1.5):
            with self.subTest(pump=pump), self.assertRaises(ValueError):
                bart.burst_or_not(pump, capacity=128)

    def test_invalid_deck_is_rejected(self):
        for deck in (0, 5, True, 1.0):
            with self.subTest(deck=deck), self.assertRaises(ValueError):
                igt.gain_loss(deck)

    def test_reset_discards_partial_decks(self):
        igt.gain_loss(1)
        igt.reset_decks()
        losses = config.igt_deck1_all_losses
        self.assertEqual(Counter(igt.gain_loss(1)[1] for _ in losses), Counter(losses))
