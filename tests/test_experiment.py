"""Exercise task outcomes with scripted input, without a display or audio device."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import main


class Stimulus:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def draw(self):
        pass


class BartFlowTests(unittest.TestCase):
    def run_frames(self, frames, burst=False, factor=None):
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
                visual=SimpleNamespace(TextStim=Stimulus, ImageStim=Stimulus),
                win=SimpleNamespace(flip=lambda: None),
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
            patch.object(main, "wait_for_space"),
            patch.object(main, "check_abort", side_effect=tick),
            patch.object(main, "burst_or_not", return_value=burst),
        ):
            main.bart_experiment()
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


class OrchestrationTests(unittest.TestCase):
    def exercise(self, *, cancel=False, window_error=None, task_error=None, export_error=None):
        from unittest.mock import Mock
        import sys

        dialog = SimpleNamespace(
            OK=not cancel,
            data=["name", "3", "Other", "25", "Right"],
            addField=lambda *a, **kw: None,
            show=lambda: None,
        )
        window = Mock(size=(1200, 675))
        movie = Mock(isFinished=True)
        results = Mock()
        results.save.side_effect = export_error
        visual = SimpleNamespace(
            Window=Mock(return_value=window, side_effect=window_error),
            TextStim=Stimulus,
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
            patch.object(main.cfg, "output_directory", "unused"),
            patch.object(main, "SessionResults", return_value=results) as factory,
            patch.object(main, "survey") as survey,
            patch.object(main, "bart_experiment", side_effect=task_error) as bart,
            patch.object(main, "igt_experiment") as igt,
            patch.object(main, "wait_for_space"),
        ):
            error = None
            try:
                main.run()
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


class IgtFlowTests(unittest.TestCase):
    def test_one_click_records_one_choice_and_updates_net_reward(self):
        from unittest.mock import Mock

        rows = []
        mouse = SimpleNamespace(
            getPressed=Mock(side_effect=[(1, 0, 0), (0, 0, 0)]), isPressedIn=Mock(return_value=True)
        )
        with (
            patch.multiple(
                main,
                create=True,
                visual=SimpleNamespace(TextStim=Stimulus, ImageStim=Stimulus, Rect=Stimulus),
                win=SimpleNamespace(flip=lambda: None),
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
            patch.object(main, "wait_for_space"),
            patch.object(main, "gain_loss", return_value=(1, 0.5)) as draw,
        ):
            main.igt_experiment()
            self.assertAlmostEqual(main.total_liquidity, 0.5)
        draw.assert_called_once_with(1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["choice"], 1)
        self.assertEqual(rows[0]["gain"], 1)
        self.assertEqual(rows[0]["loss"], 0.5)
        self.assertGreaterEqual(rows[0]["RT"], 0)
