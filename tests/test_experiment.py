"""Exercise task outcomes with scripted input, without a display or audio device."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import main
from localization import load_catalog


class Stimulus:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def draw(self):
        pass


class BartFlowTests(unittest.TestCase):
    def run_frames(self, frames, burst=False, factor=None, catalog=None):
        state = {}
        script = iter(frames)
        rows = []

        def tick():
            state.clear()
            state.update(next(script))

        with (
            patch.multiple(
                main,
                create=True,
                visual=SimpleNamespace(
                    TextStim=Stimulus, ImageStim=Stimulus, Rect=Stimulus, ShapeStim=Stimulus
                ),
                win=SimpleNamespace(flip=lambda: None, size=(1200, 675)),
                core=SimpleNamespace(wait=lambda _: None),
                keys=SimpleNamespace(getState=lambda key: state.get(key, False)),
                results=SimpleNamespace(append=rows.append),
                w=1200,
                h=675,
                font_size=20,
                distance_from_vertical_edges=90,
                distance_from_horizontal_edges=110,
                total_liquidity=0,
                sound=SimpleNamespace(Sound=Stimulus),
            ),
            patch.multiple(
                main.cfg,
                bart_total_number_of_trials=1,
                bart_blow_sound=0,
                bart_burst_sound=0,
                bart_collect_sound=0,
                bart_blowing_factor=factor or main.cfg.bart_blowing_factor,
            ),
            patch.object(main, "wait_for_advance"),
            patch.object(main, "check_abort", side_effect=tick),
            patch.object(main, "burst_or_not", return_value=burst),
        ):
            main.bart_experiment(load_catalog("fa") if catalog is None else catalog)
            return rows, main.total_liquidity

    def test_held_space_pumps_once_and_collects_on_release(self):
        rows, total = self.run_frames([{"space": True}, {"space": True}, {}, {"return": True}, {}])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pumps"], 1)
        self.assertEqual(rows[0]["explosion"], 0)
        self.assertAlmostEqual(total, main.cfg.bart_blow_addition)
        self.assertGreaterEqual(rows[0]["RT"], 0)

    def test_skip_does_not_credit_uncollected_pumps(self):
        rows, total = self.run_frames([{"space": True}, {}, {"i": True}])
        self.assertEqual(rows, [])
        self.assertEqual(total, 0)

    def test_burst_is_recorded_once_with_zero_gain(self):
        rows, total = self.run_frames([{"space": True}], burst=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["explosion"], 1)
        self.assertEqual(rows[0]["gain"], 0)
        self.assertEqual(total, 0)

    def test_burst_does_not_also_collect_pending_enter(self):
        rows, total = self.run_frames([{"return": True}, {"space": True}], burst=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(total, 0)

    def test_repeat_factor_one_pumps_each_poll(self):
        rows, total = self.run_frames(
            [{"space": True}, {"space": True}, {"return": True}, {}], factor=1
        )
        self.assertEqual(rows[0]["pumps"], 2)
        self.assertAlmostEqual(total, 2 * main.cfg.bart_blow_addition)

    def test_english_task_preserves_collection_rules(self):
        rows, total = self.run_frames(
            [{"space": True}, {}, {"return": True}, {}], catalog=load_catalog("en")
        )
        self.assertEqual(rows[0]["pumps"], 1)
        self.assertAlmostEqual(total, main.cfg.bart_blow_addition)

    def test_configured_pump_and_collect_keys_drive_input(self):
        controls = dict(main.cfg.controls, pump="p", collect="c")
        with patch.object(main.cfg, "controls", controls):
            rows, total = self.run_frames(
                [{"p": True}, {}, {"c": True}, {}], catalog=load_catalog("en")
            )
        self.assertEqual(rows[0]["pumps"], 1)
        self.assertAlmostEqual(total, main.cfg.bart_blow_addition)


class OrchestrationTests(unittest.TestCase):
    def exercise(
        self, *, cancel=False, window_error=None, task_error=None, export_error=None, catalog=None
    ):
        from unittest.mock import Mock
        import sys

        presentation = load_catalog(main.cfg.language) if catalog is None else catalog
        texts = []

        def make_text(*args, **kwargs):
            stimulus = Stimulus(*args, **kwargs)
            texts.append(stimulus)
            return stimulus

        dialog = SimpleNamespace(
            OK=not cancel,
            data=[
                "name",
                "3",
                presentation.text("choice.Other"),
                "25",
                presentation.text("choice.Right"),
            ],
            addField=lambda *a, **kw: None,
            show=lambda: None,
        )
        window = Mock(size=(1200, 675))
        movie = Mock(isFinished=True)
        results = Mock()
        results.save.side_effect = export_error
        visual = SimpleNamespace(
            Window=Mock(return_value=window, side_effect=window_error),
            TextStim=make_text,
            VlcMovieStim=Mock(return_value=movie),
        )
        psychopy = SimpleNamespace(
            visual=visual,
            event=SimpleNamespace(Mouse=Mock()),
            gui=SimpleNamespace(Dlg=lambda **kw: dialog),
            core=SimpleNamespace(wait=Mock()),
            sound=SimpleNamespace(),
        )
        keyboard = SimpleNamespace(Keyboard=Mock())
        with (
            patch.dict(
                sys.modules,
                {
                    "psychopy": psychopy,
                    "psychopy.hardware": SimpleNamespace(),
                    "psychopy.hardware.keyboard": keyboard,
                },
            ),
            patch.object(main, "prepare_config"),
            patch.object(main, "register_catalog_fonts"),
            patch.object(main.cfg, "output_directory", "unused"),
            patch.object(main, "SessionResults", return_value=results) as factory,
            patch.object(main, "survey") as survey,
            patch.object(main, "bart_experiment", side_effect=task_error) as bart,
            patch.object(main, "igt_experiment") as igt,
            patch.object(main, "wait_for_advance"),
        ):
            error = None
            try:
                main.run(catalog=catalog)
            except Exception as caught:
                error = caught
        return SimpleNamespace(
            error=error,
            results=results,
            window=window,
            movie=movie,
            factory=factory,
            survey=survey,
            bart=bart,
            igt=igt,
            texts=texts,
        )

    def test_success_runs_counterbalanced_tasks_once_and_saves(self):
        result = self.exercise()
        self.assertIsNone(result.error)
        result.bart.assert_called_once()
        result.igt.assert_called_once()
        self.assertEqual(result.survey.call_count, 2)
        result.results.save.assert_called_once()
        result.results.close.assert_called_once()
        result.window.close.assert_called_once()

    def test_cancel_does_not_create_results(self):
        result = self.exercise(cancel=True)
        self.assertIsNone(result.error)
        result.factory.assert_not_called()

    def test_task_failure_is_propagated_without_restarting(self):
        failure = RuntimeError("task failed")
        result = self.exercise(task_error=failure)
        self.assertIs(result.error, failure)
        result.bart.assert_called_once()
        result.igt.assert_not_called()
        result.results.save.assert_called_once()
        result.window.close.assert_called_once()

    def test_window_failure_does_not_mask_original_error(self):
        failure = RuntimeError("display unavailable")
        result = self.exercise(window_error=failure)
        self.assertIs(result.error, failure)
        result.results.save.assert_called_once()
        result.results.close.assert_called_once()

    def test_export_failure_still_closes_journal_and_window(self):
        failure = OSError("disk full")
        result = self.exercise(export_error=failure)
        self.assertIs(result.error, failure)
        result.results.close.assert_called_once()
        result.window.close.assert_called_once()

    def test_injected_english_catalog_reaches_every_screen_and_normalizes_metadata(self):
        from dataclasses import replace

        catalog = load_catalog("en")
        catalog = replace(
            catalog,
            font="Injected Font",
            messages=dict(
                catalog.messages,
                completion="CUSTOM: {amount:.2f} / {toman}. Press {advance_key}.",
            ),
        )
        with patch.object(main, "load_catalog", side_effect=AssertionError("must use injection")):
            result = self.exercise(catalog=catalog)
        self.assertIsNone(result.error)
        result.bart.assert_called_once_with(catalog)
        result.igt.assert_called_once_with(catalog)
        self.assertTrue(
            all(call.kwargs["catalog"] is catalog for call in result.survey.call_args_list)
        )
        record = result.results.append.call_args.args[0]
        self.assertEqual(record["gender"], "Other")
        self.assertEqual(record["handedness"], "Right")
        self.assertIn("CUSTOM:", result.texts[-1].text)
        self.assertEqual(result.texts[-1].font, "Injected Font")
        self.assertEqual(result.texts[-1].languageStyle, "LTR")

    def test_english_selection_uses_configuration(self):
        with patch.object(main.cfg, "language", "en"):
            result = self.exercise()
        self.assertIsNone(result.error)
        self.assertIn("Thank you", result.texts[-1].text)
        self.assertEqual(result.texts[-1].languageStyle, "LTR")

    def test_persian_dialog_values_remain_canonical_in_results(self):
        result = self.exercise(catalog=load_catalog("fa"))
        self.assertIsNone(result.error)
        record = result.results.append.call_args.args[0]
        self.assertEqual(record["gender"], "Other")
        self.assertEqual(record["handedness"], "Right")
        self.assertEqual(result.texts[-1].languageStyle, "Arabic")


class IgtFlowTests(unittest.TestCase):
    def run_click(self, catalog, *, deck=1, outcome=(1, 0.5), outside_first=False):
        from unittest.mock import Mock

        rows = []
        mouse = SimpleNamespace(
            getPressed=Mock(side_effect=[(1, 0, 0), (0, 0, 0)] * (2 if outside_first else 1)),
            isPressedIn=Mock(
                side_effect=([False] * 4 if outside_first else []) + [False] * (deck - 1) + [True]
            ),
        )
        with (
            patch.multiple(
                main,
                create=True,
                visual=SimpleNamespace(
                    TextStim=Stimulus, ImageStim=Stimulus, Rect=Stimulus, ShapeStim=Stimulus
                ),
                win=SimpleNamespace(flip=lambda: None, size=(1200, 675)),
                core=SimpleNamespace(wait=lambda _: None),
                keys=SimpleNamespace(getState=lambda _: False),
                results=SimpleNamespace(append=rows.append),
                myMouse=mouse,
                w=1200,
                h=675,
                font_size=20,
                distance_from_vertical_edges=90,
                distance_from_horizontal_edges=110,
                total_liquidity=0,
            ),
            patch.multiple(main.cfg, igt_total_number_of_trials=1, igt_sleep_time=0),
            patch.object(main, "wait_for_advance"),
            patch.object(main, "gain_loss", return_value=outcome) as draw,
        ):
            main.igt_experiment(catalog)
            self.assertAlmostEqual(main.total_liquidity, outcome[0] - outcome[1])
        draw.assert_called_once_with(deck)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["choice"], deck)
        self.assertEqual(rows[0]["gain"], outcome[0])
        self.assertEqual(rows[0]["loss"], outcome[1])
        self.assertGreaterEqual(rows[0]["RT"], 0)

    def test_one_click_records_one_choice_and_updates_net_reward(self):
        for language in ("fa", "en"):
            with self.subTest(language=language):
                self.run_click(load_catalog(language))

    def test_outside_click_does_not_consume_an_outcome_or_record_a_trial(self):
        self.run_click(load_catalog("en"), deck=3, outside_first=True)

    def test_all_decks_and_zero_or_negative_net_outcomes_keep_original_values(self):
        for deck, outcome in ((1, (1, 0)), (2, (1, 12.5)), (3, (0.5, 0.5)), (4, (0.5, 0))):
            with self.subTest(deck=deck):
                self.run_click(load_catalog("en"), deck=deck, outcome=outcome)
