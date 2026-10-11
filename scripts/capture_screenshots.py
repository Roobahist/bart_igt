"""Capture real English PsychoPy frames with deterministic demonstration input.

Run only in an isolated environment with PsychoPy and a display (e.g. CI/Xvfb).
This exercises the application's existing task/survey renderers, not human input,
audio, movie playback or calibrated timing. No participant information is used.
"""

import argparse
import json
import os
from pathlib import Path
import platform
import random
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main  # noqa: E402
from localization import load_catalog  # noqa: E402
from session import prepare_config  # noqa: E402


class DemoInput:
    """Script press/release states while leaving rendering and task rules real."""

    def __init__(self, frames, *, target):
        self.frames = iter(frames)
        self.state = {}
        self.target = target

    def tick(self):
        self.state = next(self.frames)

    def getState(self, key):
        return self.state.get(key, False)

    def getPressed(self, **kwargs):
        return (int(self.state.get("mouse", False)), 0, 0)

    def isPressedIn(self, stimulus):
        return self.target(stimulus)


def capture(directory):
    import psychopy
    from psychopy import core, visual

    catalog = load_catalog("en")
    prepare_config(main.cfg, needs_number_images=False)
    directory.mkdir(parents=True, exist_ok=True)
    window = visual.Window(
        fullscr=False,
        color=main.cfg.igt_bg_color,
        units="pix",
        size=[1200, 675],
        checkTiming=False,
        waitBlanking=False,
        allowGUI=False,
        gammaErrorPolicy="warn",
    )
    main.visual, main.core, main.win = visual, core, window
    main.w, main.h = window.size
    main.font_size = main.w * 0.0175 + 0.371
    main.distance_from_vertical_edges = main.w / 13
    main.distance_from_horizontal_edges = 1.2 * main.distance_from_vertical_edges
    main.total_liquidity = 0
    rows = []
    main.results = type("DemoResults", (), {"append": staticmethod(rows.append)})()
    phase, frame_number = "", 0
    captures = []
    schedule = {
        "survey": {1: "sam-survey", 3: "sam-selected"},
        "igt": {1: "igt-instructions", 2: "igt-choice", 3: "igt-feedback"},
        "bart": {1: "bart-instructions", 22: "bart-balloon"},
    }
    original_flip = window.flip

    def flip(*args, **kwargs):
        nonlocal frame_number
        frame_number += 1
        name = schedule[phase].get(frame_number)
        if name:
            # The back buffer contains the real rendered frame about to be displayed.
            # Capture before swapping; Xvfb front-buffer reads can be unreliable.
            frame = window.getMovieFrame(buffer="back")
            frame.save(directory / f"{name}.png")
            window.movieFrames.clear()
            captures.append(name)
        return original_flip(*args, **kwargs)

    window.flip = flip
    try:
        phase = "survey"
        inputs = DemoInput(
            [{"mouse": True}, {"space": True}, {}], target=lambda stimulus: stimulus.pos[0] == 0
        )
        main.keys = main.myMouse = inputs
        with patch.object(main, "check_abort", side_effect=inputs.tick):
            main.survey("before video", catalog)

        phase, frame_number = "igt", 0
        inputs = DemoInput(
            [
                state
                for _ in range(main.cfg.igt_total_number_of_trials)
                for state in ({"mouse": True}, {})
            ],
            target=lambda stimulus: stimulus.pos[0] < -main.w / 4,
        )
        main.keys = main.myMouse = inputs
        main.reset_decks()
        random.seed(1)
        with (
            patch.object(main, "check_abort", side_effect=inputs.tick),
            patch.object(main, "wait_for_advance"),
            patch.object(main.cfg, "igt_sleep_time", 0),
        ):
            main.igt_experiment(catalog)

        phase, frame_number = "bart", 0
        inputs = DemoInput(
            [state for _ in range(20) for state in ({"space": True}, {})] + [{"return": True}, {}],
            target=lambda stimulus: False,
        )
        main.keys = inputs
        random.seed(1)  # This actual burst distribution survives the 20 scripted pumps.
        with (
            patch.object(main, "check_abort", side_effect=inputs.tick),
            patch.object(main, "wait_for_advance"),
            patch.multiple(
                main.cfg,
                bart_total_number_of_trials=1,
                bart_blow_sound=0,
                bart_burst_sound=0,
                bart_collect_sound=0,
            ),
        ):
            main.bart_experiment(catalog)

        assert len(captures) == 7, captures
        assert rows[0] == {"arousal": 5, "pleasure": 5, "section": "before video"}
        assert (
            len([row for row in rows if row["section"] == "IGT"])
            == main.cfg.igt_total_number_of_trials
        )
        assert rows[-1]["section"] == "BART" and rows[-1]["pumps"] == 20
        assert rows[-1]["explosion"] == 0
        provenance = {
            "description": "Real PsychoPy OpenGL frames, automated demonstration input; no participant session",
            "language": "en",
            "psychopy": psychopy.__version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_commit": os.environ.get("GITHUB_SHA"),
            "workflow_run": os.environ.get("GITHUB_RUN_ID"),
            "capture_method": "Window.getMovieFrame(back) before actual Window.flip",
            "screenshots": captures,
            "demo_settings": {
                "igt_trials": main.cfg.igt_total_number_of_trials,
                "bart_trials": 1,
                "bart_pumps": 20,
                "seed": 1,
                "sound": False,
                "igt_feedback_wait": 0,
            },
            "not_verified": [
                "physical input",
                "hardware timing",
                "audio",
                "VLC video",
                "participant dialog",
            ],
            "synthetic_responses": rows,
        }
        (directory / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    finally:
        window.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/screenshots")
    capture(parser.parse_args().output)
