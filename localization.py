"""Load injectable presentation catalogs without depending on PsychoPy."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
from string import Formatter
from typing import Mapping

LOCALES_DIRECTORY = Path(__file__).resolve().parent / "locales"


@dataclass(frozen=True)
class LanguageCatalog:
    """Text and rendering settings injected into one participant session."""

    messages: Mapping[str, str]
    font: str
    language_style: str
    rating_image_pattern: str | None
    rating_colors: Mapping[str, list[float]]
    display_font: str | None = None
    font_files: tuple[str, ...] = ()

    def text(self, key: str, **values) -> str:
        """Render a message using live study values, rather than baked-in counts."""
        try:
            return self.messages[key].format(**values)
        except (KeyError, ValueError) as error:
            raise ValueError(f"Cannot render catalog message {key!r}: {error}") from error

    def validate(self):
        """Check coverage and template parameters before participant collection."""
        reference = json.loads((LOCALES_DIRECTORY / "en.json").read_text(encoding="utf-8"))[
            "messages"
        ]
        missing = set(reference) - set(self.messages)
        if missing:
            raise ValueError("Catalog is missing messages: " + ", ".join(sorted(missing)))
        formatter = Formatter()
        for key, template in reference.items():
            required = {field for _, field, _, _ in formatter.parse(template) if field is not None}
            actual = {
                field for _, field, _, _ in formatter.parse(self.messages[key]) if field is not None
            }
            if actual != required:
                raise ValueError(f"Catalog message {key!r} must use parameters {sorted(required)}")

    @property
    def is_rtl(self) -> bool:
        return self.language_style in ("Arabic", "RTL")

    @property
    def text_options(self) -> dict[str, str]:
        """PsychoPy text options for this catalog's script and font."""
        return {"font": self.font, "languageStyle": self.language_style}


def load_catalog(language: str, *, directory: Path = LOCALES_DIRECTORY) -> LanguageCatalog:
    """Read a locale JSON file; unknown or malformed catalogs fail explicitly."""
    if not isinstance(language, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", language):
        raise ValueError("language must be a locale name such as fa or en")
    path = Path(directory) / f"{language}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Language catalog not found: {language}") from error
    messages = data.get("messages")
    if (
        not isinstance(messages, dict)
        or not messages
        or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in messages.items()
        )
    ):
        raise ValueError("Catalog messages must be a nonempty map of strings")
    if not isinstance(data.get("font"), str) or not data["font"]:
        raise ValueError("Catalog font must be a nonempty string")
    if data.get("language_style") not in ("Arabic", "RTL", "LTR"):
        raise ValueError("Catalog language_style must be Arabic, RTL or LTR")
    pattern = data.get("rating_image_pattern")
    if pattern is not None and not isinstance(pattern, str):
        raise ValueError("rating_image_pattern must be a string or null")
    colors = data.get("rating_colors", {})
    for state in ("selected", "unselected"):
        color = colors.get(state)
        if (
            not isinstance(color, list)
            or len(color) != 3
            or not all(isinstance(value, (int, float)) and -1 <= value <= 1 for value in color)
        ):
            raise ValueError(f"Catalog rating_colors.{state} must be a normalized RGB triplet")
    display_font = data.get("display_font")
    if display_font is not None and (not isinstance(display_font, str) or not display_font):
        raise ValueError("display_font must be a nonempty string or null")
    files = data.get("font_files", [])
    if not isinstance(files, list) or not all(isinstance(path, str) and path for path in files):
        raise ValueError("font_files must be a list of nonempty paths")
    catalog = LanguageCatalog(
        messages, data["font"], data["language_style"], pattern, colors, display_font, tuple(files)
    )
    catalog.validate()
    return catalog


def register_catalog_fonts(catalog):
    """Register bundled faces in this process only, without OS font installation."""
    if not catalog.font_files:
        return
    paths = [LOCALES_DIRECTORY.parent / path for path in catalog.font_files]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing catalog font files: " + ", ".join(missing))
    from pyglet import font

    for path in paths:
        font.add_file(str(path))
