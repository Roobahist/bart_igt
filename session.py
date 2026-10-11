"""Session ordering, startup checks and recoverable local result storage."""

import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
import tempfile
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent
REQUIRED_COLUMNS = {
    "subjectName",
    "subjectCode",
    "gender",
    "age",
    "handedness",
    "video",
    "section",
    "arousal",
    "pleasure",
    "trial",
    "choice",
    "gain",
    "loss",
    "RT",
    "pumps",
    "explosion",
}


def task_order(subject_code):
    """Counterbalance odd numeric codes; use IGT first for other codes."""
    try:
        odd = int(subject_code) % 2
    except (ValueError, TypeError):
        odd = False
    return ("BART", "IGT") if odd else ("IGT", "BART")


def prepare_config(cfg, *, needs_number_images=True):
    """Validate study settings and resolve assets against the repository root."""
    if (
        len(cfg.column_order) != len(set(cfg.column_order))
        or set(cfg.column_order) != REQUIRED_COLUMNS
    ):
        raise ValueError("column_order must contain each original result column exactly once")
    for name in ("bart_max_balloon_capacity", "bart_blowing_factor"):
        value = getattr(cfg, name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    for name in ("igt_total_number_of_trials", "bart_total_number_of_trials"):
        value = getattr(cfg, name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    for name in (
        "dollar_toman",
        "fixation_sleep_time",
        "igt_initial_liquidity",
        "igt_sleep_time",
        "bart_blow_addition",
    ):
        _nonnegative(getattr(cfg, name), name)
    for deck in range(1, 5):
        _nonnegative(getattr(cfg, f"igt_deck{deck}_gain"), f"deck {deck} gain")
        losses = getattr(cfg, f"igt_deck{deck}_all_losses")
        if not losses:
            raise ValueError(f"deck {deck} needs at least one loss")
        for loss in losses:
            _nonnegative(loss, f"deck {deck} loss")

    control_names = {"advance", "pump", "collect", "skip", "replay", "pause", "abort"}
    if set(cfg.controls) != control_names or not all(
        isinstance(value, str) and value for value in cfg.controls.values()
    ):
        raise ValueError("controls must define a nonempty key name for every experiment action")

    paths = [name for name in vars(cfg) if name.endswith("_path")]
    required = [name for name in paths if name.startswith(("arousal_", "pleasure_", "number"))]
    if not needs_number_images:
        required = [name for name in required if not name.startswith("number")]
    required.append("video_path")
    if not cfg.igt_skip:
        required += ["igt_card_back_path", "igt_card_front_path"]
    if not cfg.bart_skip:
        required += ["bart_rope_path", "bart_balloon_path"]
        for name in ("blow", "burst", "collect"):
            if getattr(cfg, f"bart_{name}_sound"):
                required.append(f"bart_{name}_path")
    for name in paths:
        setattr(cfg, name, str(PROJECT_ROOT / getattr(cfg, name)))
    missing = [name for name in required if not Path(getattr(cfg, name)).is_file()]
    if missing:
        raise FileNotFoundError("Missing experiment assets: " + ", ".join(missing))
    cfg.output_directory = str(PROJECT_ROOT / cfg.output_directory)


def _nonnegative(value, name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(f"{name} must be finite and nonnegative")


def write_workbook(path, columns, rows):
    """Atomically export exact column order; participant strings stay literal."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Results"
    sheet.append(list(columns))
    for row in rows:
        sheet.append([row.get(column) for column in columns])
        # Excel interprets leading '=' as formulas unless explicitly stored as text.
        for cell in sheet[sheet.max_row]:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix=".xlsx")
    os.close(descriptor)
    try:
        workbook.save(temporary)
        os.replace(temporary, path)
    finally:
        workbook.close()
        Path(temporary).unlink(missing_ok=True)


class SessionResults:
    """Append each response to a private, flushed journal before Excel export."""

    def __init__(self, directory, columns):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.columns = list(columns)
        self.rows = []
        stem = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex
        self.path = directory / (stem + ".xlsx")
        self.journal_path = self.path.with_suffix(".jsonl")
        fd = os.open(self.journal_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self._journal = os.fdopen(fd, "w", encoding="utf-8")
        self._write({"columns": self.columns})

    def _write(self, value):
        self._journal.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        self._journal.flush()
        os.fsync(self._journal.fileno())

    def append(self, row):
        """Durably retain a completed trial or survey with its original fields."""
        unknown = set(row) - set(self.columns)
        if unknown:
            raise ValueError("Unknown result fields: " + ", ".join(sorted(unknown)))
        self._write(row)
        self.rows.append(dict(row))

    def save(self):
        write_workbook(self.path, self.columns, self.rows)
        return self.path

    def close(self):
        self._journal.close()


def recover(journal_path):
    """Export a journal, tolerating only an incomplete final crash-write line."""
    journal_path = Path(journal_path)
    lines = journal_path.read_text(encoding="utf-8").splitlines(keepends=True)
    columns = json.loads(lines[0])["columns"]
    rows = []
    for index, line in enumerate(lines[1:], 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1 or line.endswith("\n"):
                raise
    target = journal_path.with_name(journal_path.stem + "-recovered.xlsx")
    write_workbook(target, columns, rows)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recover Excel results from a session journal")
    parser.add_argument("journal", type=Path)
    print(recover(parser.parse_args().journal))
