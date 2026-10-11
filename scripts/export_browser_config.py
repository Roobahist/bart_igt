"""Export existing study settings for the build-free browser runtime."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config as cfg  # noqa: E402


def browser_config():
    if cfg.bart_blowing_factor != sys.maxsize:
        raise ValueError("Browser requires fresh pumps: set bart_blowing_factor to sys.maxsize")
    return {
        "schema": 1,
        "language": "en",
        "columns": cfg.column_order,
        "controls": cfg.controls,
        "fullscreen": cfg.fullscreen,
        "fixationMs": cfg.fixation_sleep_time * 1000,
        "exchangeRate": cfg.dollar_toman,
        "video": {"name": cfg.video_name, "path": "../" + cfg.video_path},
        "igt": {
            "skip": bool(cfg.igt_skip),
            "trials": cfg.igt_total_number_of_trials,
            "initialBalance": cfg.igt_initial_liquidity,
            "feedbackMs": cfg.igt_sleep_time * 1000,
            "decks": [
                {
                    "gain": getattr(cfg, f"igt_deck{deck}_gain"),
                    "losses": getattr(cfg, f"igt_deck{deck}_all_losses"),
                }
                for deck in range(1, 5)
            ],
        },
        "bart": {
            "skip": bool(cfg.bart_skip),
            "trials": cfg.bart_total_number_of_trials,
            "capacity": cfg.bart_max_balloon_capacity,
            "reward": cfg.bart_blow_addition,
            "repeatPumps": False,
            "sounds": {
                name: {
                    "enabled": bool(getattr(cfg, f"bart_{name}_sound")),
                    "path": "../" + getattr(cfg, f"bart_{name}_path"),
                }
                for name in ("blow", "burst", "collect")
            },
        },
        "sam": {
            kind: ["../" + getattr(cfg, f"{kind}_{number}_path") for number in range(1, 6)]
            for kind in ("arousal", "pleasure")
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "web" / "study-config.json"
    content = json.dumps(browser_config(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not target.is_file() or target.read_text() != content:
            raise SystemExit(
                "Regenerate web/study-config.json with scripts/export_browser_config.py"
            )
    else:
        target.write_text(content, encoding="utf-8")
