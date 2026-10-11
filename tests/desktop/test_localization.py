"""Catalog coverage, live template values and language-specific rating controls."""

import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from study import settings as config
from apps.desktop.localization import load_catalog
from apps.desktop import experiment as main
from apps.desktop.results import prepare_config
from test_experiment import Stimulus


class CatalogTests(unittest.TestCase):
    def test_bundled_catalogs_cover_the_same_messages(self):
        english, persian = load_catalog("en"), load_catalog("fa")
        self.assertEqual(set(english.messages), set(persian.messages))
        self.assertFalse(english.is_rtl)
        self.assertTrue(persian.is_rtl)
        for catalog in (english, persian):
            catalog.validate()
            self.assertIn("13", catalog.text("igt_instructions", trials=13, advance_key="A"))
            self.assertIn("A", catalog.text("continue", advance_key="A"))
            self.assertIn("1.25", catalog.text("balloon_value", amount=1.25))
            self.assertIn("07", catalog.text("balloon_trial", number=7))
            self.assertIn(
                "P",
                catalog.text("bart_instructions", pump_key="P", collect_key="C", advance_key="A"),
            )

    def test_missing_message_or_parameter_is_rejected(self):
        english = load_catalog("en")
        messages = dict(english.messages)
        del messages["completion"]
        with self.assertRaisesRegex(ValueError, "missing messages"):
            replace(english, messages=messages).validate()
        messages = dict(english.messages, completion="Wrong {unprovided}")
        with self.assertRaisesRegex(ValueError, "parameters"):
            replace(english, messages=messages).validate()
        with self.assertRaisesRegex(ValueError, "Cannot render"):
            english.text("balloon_value")

    def test_unknown_or_unsafe_locale_names_are_rejected(self):
        for value in ("unknown", "../en", "/en", ""):
            with self.subTest(locale=value), self.assertRaises(ValueError):
                load_catalog(value)

    def test_custom_catalog_directory_and_font_are_supported(self):
        original = json.loads(
            (Path(main.__file__).resolve().parents[2] / "study/locales/en.json").read_text()
        )
        original["font"] = "Custom Font"
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "custom.json").write_text(json.dumps(original))
            self.assertEqual(load_catalog("custom", directory=Path(directory)).font, "Custom Font")

    def test_english_asset_checks_do_not_require_persian_digit_images(self):
        cfg = SimpleNamespace(
            **{
                key: copy.deepcopy(value)
                for key, value in vars(config).items()
                if not key.startswith("_") and key != "sys"
            }
        )
        cfg.number1_unselected_path = "intentionally-missing.png"
        prepare_config(cfg, needs_number_images=False)
        with self.assertRaises(FileNotFoundError):
            prepare_config(cfg, needs_number_images=True)

    def test_english_ratings_have_latin_labels_and_equal_hit_areas(self):
        catalog = load_catalog("en")
        with patch.multiple(
            main,
            create=True,
            visual=SimpleNamespace(Rect=Stimulus, TextStim=Stimulus),
            win=object(),
        ):
            targets, labels = main.make_rating_row(catalog, 20, [40, 40], 50)
            self.assertEqual([label.text for label in labels], list("123456789"))
            self.assertTrue(all(target.width == 40 and target.height == 40 for target in targets))
            self.assertEqual([target.pos[0] for target in targets], list(range(-200, 201, 50)))
            main.update_rating_selection(catalog, targets, 4)
            self.assertEqual(targets[3].fillColor, catalog.rating_colors["selected"])
            self.assertEqual(targets[0].fillColor, catalog.rating_colors["unselected"])

    def test_persian_ratings_keep_existing_image_assets(self):
        catalog = load_catalog("fa")
        with patch.multiple(
            main, create=True, visual=SimpleNamespace(ImageStim=Stimulus), win=object()
        ):
            targets, labels = main.make_rating_row(catalog, 20, [40, 40], 50)
            self.assertEqual(labels, [])
            self.assertEqual(targets[0].image, config.number1_unselected_path)
            main.update_rating_selection(catalog, targets, 4)
            self.assertEqual(targets[3].image, config.number4_selected_path)
            self.assertEqual(targets[0].image, config.number1_unselected_path)

    def test_both_surveys_complete_with_identical_recorded_ordinals(self):
        for language in ("en", "fa"):
            with self.subTest(language=language):
                rows = []
                state = {}
                frames = iter([{"mouse": 1}, {"advance": True}, {}])

                def next_frame():
                    state.clear()
                    state.update(next(frames))

                mouse = SimpleNamespace(
                    getPressed=lambda **kwargs: (state.get("mouse", 0), 0, 0),
                    isPressedIn=lambda target: target.pos[0] == 0,
                )
                with (
                    patch.multiple(
                        main,
                        create=True,
                        visual=SimpleNamespace(
                            TextStim=Stimulus, ImageStim=Stimulus, Rect=Stimulus
                        ),
                        win=SimpleNamespace(flip=lambda: None),
                        myMouse=mouse,
                        keys=SimpleNamespace(getState=lambda key: state.get("advance", False)),
                        results=SimpleNamespace(append=rows.append),
                        w=1200,
                        h=675,
                        font_size=20,
                        distance_from_horizontal_edges=110,
                    ),
                    patch.object(main, "check_abort", side_effect=next_frame),
                ):
                    main.survey("before video", load_catalog(language))
                self.assertEqual(rows, [{"arousal": 5, "pleasure": 5, "section": "before video"}])
