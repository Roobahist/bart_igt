"""Bilingual SAM, IGT and BART desktop experiment. Run with PsychoPy Coder."""

import time
import logging

import config as cfg
from igt import gain_loss, reset_decks
from bart import burst_or_not
from session import SessionResults, task_order, prepare_config
from localization import load_catalog

PARTICIPANT_FIELDS = ("subjectName", "subjectCode", "gender", "age", "handedness")
PARTICIPANT_CHOICES = {"gender": ("Male", "Female", "Other"), "handedness": ("Right", "Left")}


class ExperimentAborted(Exception):
    """Operator requested a safe session stop."""


def check_abort():
    if keys.getState(cfg.controls["abort"]):
        raise ExperimentAborted()


def wait_for_advance():
    """Wait for a fresh press, so held instruction keys do not pump balloons."""
    while keys.getState(cfg.controls["advance"]):
        check_abort()
        core.wait(0.001)
    while not keys.getState(cfg.controls["advance"]):
        check_abort()
        core.wait(0.001)
    while keys.getState(cfg.controls["advance"]):
        check_abort()
        core.wait(0.001)


def igt_experiment(catalog):
    global total_liquidity

    if not cfg.igt_skip:
        igt_Liquidity = cfg.igt_initial_liquidity

        # Instruction

        text = visual.TextStim(
            win=win,
            text=catalog.text(
                "igt_instructions",
                trials=cfg.igt_total_number_of_trials,
                advance_key=cfg.controls["advance"].upper(),
            ),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )
        text.draw()
        win.flip()
        wait_for_advance()

        # Experiment

        trial_number = 1

        card_width = 2 * w / 13
        card_height = 1.5 * card_width
        cards_distance = w / 13

        card1_img_pos = [
            -(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card2_img_pos = [
            -(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card3_img_pos = [
            +(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card4_img_pos = [
            +(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]

        card1_img = visual.ImageStim(
            win, image=cfg.igt_card_back_path, size=[card_width, card_height], pos=card1_img_pos
        )
        card2_img = visual.ImageStim(
            win, image=cfg.igt_card_back_path, size=[card_width, card_height], pos=card2_img_pos
        )
        card3_img = visual.ImageStim(
            win, image=cfg.igt_card_back_path, size=[card_width, card_height], pos=card3_img_pos
        )
        card4_img = visual.ImageStim(
            win, image=cfg.igt_card_back_path, size=[card_width, card_height], pos=card4_img_pos
        )

        card1_back_img_pos = [
            -(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card2_back_img_pos = [
            -(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card3_back_img_pos = [
            +(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]
        card4_back_img_pos = [
            +(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (card_height / 2) - distance_from_horizontal_edges),
        ]

        card1_back_img = visual.ImageStim(
            win,
            image=cfg.igt_card_front_path,
            size=[card_width, card_height],
            pos=card1_back_img_pos,
        )
        card2_back_img = visual.ImageStim(
            win,
            image=cfg.igt_card_front_path,
            size=[card_width, card_height],
            pos=card2_back_img_pos,
        )
        card3_back_img = visual.ImageStim(
            win,
            image=cfg.igt_card_front_path,
            size=[card_width, card_height],
            pos=card3_back_img_pos,
        )
        card4_back_img = visual.ImageStim(
            win,
            image=cfg.igt_card_front_path,
            size=[card_width, card_height],
            pos=card4_back_img_pos,
        )

        card1_text_pos = [
            -(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (distance_from_horizontal_edges / 2)),
        ]
        card2_text_pos = [
            -(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (distance_from_horizontal_edges / 2)),
        ]
        card3_text_pos = [
            +(0.5 * card_width + 0.5 * cards_distance),
            -(h / 2 - (distance_from_horizontal_edges / 2)),
        ]
        card4_text_pos = [
            +(1.5 * card_width + 1.5 * cards_distance),
            -(h / 2 - (distance_from_horizontal_edges / 2)),
        ]

        card1_text = visual.TextStim(
            win=win,
            text=catalog.text("deck", number=1),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=card1_text_pos,
        )
        card2_text = visual.TextStim(
            win=win,
            text=catalog.text("deck", number=2),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=card2_text_pos,
        )
        card3_text = visual.TextStim(
            win=win,
            text=catalog.text("deck", number=3),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=card3_text_pos,
        )
        card4_text = visual.TextStim(
            win=win,
            text=catalog.text("deck", number=4),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=card4_text_pos,
        )

        trial_text_pos = [
            -((1 if catalog.is_rtl else 2) * card_width + 1.5 * cards_distance),
            h / 2 - (distance_from_horizontal_edges / 2),
        ]
        trial_text = visual.TextStim(
            win=win,
            text=catalog.text("igt_trial"),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=trial_text_pos,
            anchorHoriz="right" if catalog.is_rtl else "left",
            alignText="right" if catalog.is_rtl else "left",
        )

        trial_number_text_pos = [
            -((2 if catalog.is_rtl else 1) * card_width + 1.5 * cards_distance),
            h / 2 - (distance_from_horizontal_edges / 2),
        ]
        trial_number_text = visual.TextStim(
            win=win,
            text=str(trial_number).zfill(3),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=trial_number_text_pos,
            anchorHoriz="left" if catalog.is_rtl else "right",
            alignText="left" if catalog.is_rtl else "right",
        )

        score_text_pos = [
            +((2 if catalog.is_rtl else 1.5) * card_width + 1.5 * cards_distance),
            h / 2 - (distance_from_horizontal_edges / 2),
        ]
        score_text = visual.TextStim(
            win=win,
            text=catalog.text("igt_balance"),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=score_text_pos,
            anchorHoriz="right",
            alignText="right",
        )

        score_value_text_pos = [
            +((1.5 if catalog.is_rtl else 2) * card_width + 1.5 * cards_distance),
            h / 2 - (distance_from_horizontal_edges / 2),
        ]
        score_value_text = visual.TextStim(
            win=win,
            text=catalog.text("igt_amount", amount=igt_Liquidity),
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=score_value_text_pos,
            anchorHoriz="right",
            alignText="right",
        )

        win_text_pos = [0, h / 4 + distance_from_horizontal_edges / 4]
        win_text = visual.TextStim(
            win=win,
            text="",
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=win_text_pos,
        )

        lose_text_pos = [0, h / 4 - distance_from_horizontal_edges / 4]
        lose_text = visual.TextStim(
            win=win,
            text="",
            color=cfg.igt_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
            pos=lose_text_pos,
        )

        win_rect_pos = [0, h / 4 + distance_from_horizontal_edges / 4]
        win_rect = visual.Rect(
            win=win,
            units="pix",
            width=w / 3,
            height=0.9 * (distance_from_horizontal_edges / 2),
            fillColor=[0, 1, 0],
            lineColor=[1, 1, 1],
            pos=win_rect_pos,
        )

        lose_rect_pos = [0, h / 4 - distance_from_horizontal_edges / 4]
        lose_rect = visual.Rect(
            win=win,
            units="pix",
            width=w / 3,
            height=0.9 * (distance_from_horizontal_edges / 2),
            fillColor=[1, 0, 0],
            lineColor=[1, 1, 1],
            pos=lose_rect_pos,
        )

        def draw_main():
            card1_img.draw()
            card2_img.draw()
            card3_img.draw()
            card4_img.draw()

            card1_text.draw()
            card2_text.draw()
            card3_text.draw()
            card4_text.draw()

            trial_text.draw()
            score_text.draw()
            trial_number_text.draw()
            score_value_text.draw()

        mouse_status = "UP"
        break_break = 0
        click_on_card = 0
        sleep = 0
        last_time = time.perf_counter()

        while (trial_number <= cfg.igt_total_number_of_trials) and (not break_break):
            check_abort()
            if keys.getState(cfg.controls["skip"]):
                break_break = 1

            draw_main()

            buttons = myMouse.getPressed(getTime=False)

            if mouse_status == "UP" and buttons[0] == 1:
                mouse_status = "DOWN"
                if myMouse.isPressedIn(card1_img):
                    click_on_card = 1
                    gain, loss = gain_loss(1)

                elif myMouse.isPressedIn(card2_img):
                    click_on_card = 2
                    gain, loss = gain_loss(2)

                elif myMouse.isPressedIn(card3_img):
                    click_on_card = 3
                    gain, loss = gain_loss(3)

                elif myMouse.isPressedIn(card4_img):
                    click_on_card = 4
                    gain, loss = gain_loss(4)

            if mouse_status == "DOWN" and buttons[0] == 0:
                mouse_status = "UP"

                if click_on_card > 0:
                    trial_info = {
                        "section": "IGT",
                        "trial": trial_number,
                        "choice": click_on_card,
                        "gain": gain,
                        "loss": loss,
                        "RT": time.perf_counter() - last_time,
                    }
                    results.append(trial_info)

                    sleep = 1
                    if gain > 0:
                        win_text.text = catalog.text("igt_gain", amount=gain)
                        win_rect.draw()
                        win_text.draw()

                    if loss > 0:
                        lose_text.text = catalog.text("igt_loss", amount=loss)
                        lose_rect.draw()
                        lose_text.draw()

                    if click_on_card == 1:
                        card1_back_img.draw()
                    elif click_on_card == 2:
                        card2_back_img.draw()
                    elif click_on_card == 3:
                        card3_back_img.draw()
                    elif click_on_card == 4:
                        card4_back_img.draw()

                    click_on_card = 0

            win.flip()

            if sleep:
                sleep = 0
                core.wait(cfg.igt_sleep_time)
                igt_Liquidity = igt_Liquidity + gain - loss
                score_value_text.text = catalog.text("igt_amount", amount=igt_Liquidity)
                trial_number += 1
                trial_number_text.text = str(trial_number).zfill(3)
                last_time = time.perf_counter()

        total_liquidity += igt_Liquidity - cfg.igt_initial_liquidity


def bart_experiment(catalog):
    global total_liquidity

    if not cfg.bart_skip:
        # Instructions

        instruction_text = visual.TextStim(
            win=win,
            text=catalog.text(
                "bart_instructions",
                pump_key=cfg.controls["pump"].upper(),
                collect_key=cfg.controls["collect"].upper(),
                advance_key=cfg.controls["advance"].upper(),
            ),
            color=cfg.bart_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )

        instruction_text.draw()
        win.flip()
        wait_for_advance()

        sounds = {
            name: sound.Sound(path)
            for name, enabled, path in (
                ("blow", cfg.bart_blow_sound, cfg.bart_blow_path),
                ("burst", cfg.bart_burst_sound, cfg.bart_burst_path),
                ("collect", cfg.bart_collect_sound, cfg.bart_collect_path),
            )
            if enabled
        }

        # Experiment

        min_balloon_size = [w / 40, h / 20]
        max_balloon_size = [w / 2, h]

        rope_img_pos = [0, -h / 2]
        balloon_img_pos = [0, -113 * h / 280]
        rope_img = visual.ImageStim(
            win=win, image=cfg.bart_rope_path, units="pix", pos=rope_img_pos, size=[w / 11, h / 7]
        )
        balloon_img = visual.ImageStim(
            win=win,
            image=cfg.bart_balloon_path,
            units="pix",
            pos=balloon_img_pos,
            size=min_balloon_size,
        )

        def balloon_pos_size_calculator(blow_num):

            balloon_size = [
                min_balloon_size[0]
                + (
                    (blow_num)
                    * ((max_balloon_size[0] - min_balloon_size[0]) / cfg.bart_max_balloon_capacity)
                ),
                min_balloon_size[1]
                + (
                    (blow_num)
                    * ((max_balloon_size[1] - min_balloon_size[1]) / cfg.bart_max_balloon_capacity)
                ),
            ]
            balloon_pos = [0, (-3 * h / 7) + balloon_size[1] / 2]

            return balloon_size, balloon_pos

        current_bank_text = visual.TextStim(
            win=win,
            text=catalog.text("balloon_value", amount=0),
            pos=[0, 0],
            color=cfg.bart_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )

        trial_number_text = visual.TextStim(
            win=win,
            text=catalog.text("balloon_trial", number=1),
            pos=[
                -(w / 2 - (distance_from_vertical_edges)),
                (-h / 2) + distance_from_vertical_edges,
            ],
            anchorHoriz="left",
            alignText="left",
            color=cfg.bart_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )

        main_bank_text = visual.TextStim(
            win=win,
            text=catalog.text("bank_balance", amount=0),
            pos=[(w / 2) - distance_from_vertical_edges, (-h / 2) + distance_from_vertical_edges],
            anchorHoriz="right",
            alignText="right",
            color=cfg.bart_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )

        trial_number = 1
        main_liquidity = 0
        break_break = 0
        space_status = "UP"
        return_status = "UP"

        while (trial_number <= cfg.bart_total_number_of_trials) and (not break_break):
            blow_num = 0
            bursted = 0
            collected = 0
            current_liquidity = 0
            space_counter = 0

            balloon_img.size = min_balloon_size
            balloon_img.pos = balloon_img_pos
            current_bank_text.text = catalog.text("balloon_value", amount=0)
            trial_number_text.text = catalog.text("balloon_trial", number=trial_number)

            rope_img.draw()
            balloon_img.draw()
            current_bank_text.draw()
            trial_number_text.draw()
            main_bank_text.draw()

            win.flip()
            last_time = time.perf_counter()

            while (not collected) and (not bursted) and (not break_break):
                check_abort()
                core.wait(0.001)

                if keys.getState(cfg.controls["pump"]):
                    space_status = "DOWN"

                    space_counter += 1
                    if (space_counter - 1) % cfg.bart_blowing_factor == 0:
                        blow_num += 1
                        if not burst_or_not(blow_num):
                            balloon_size, balloon_pos = balloon_pos_size_calculator(blow_num)

                            balloon_img.size = balloon_size
                            balloon_img.pos = balloon_pos

                            current_liquidity = blow_num * cfg.bart_blow_addition
                            current_bank_text.text = catalog.text(
                                "balloon_value", amount=current_liquidity
                            )

                            if cfg.bart_blow_sound:
                                sounds["blow"].play()

                            rope_img.draw()
                            balloon_img.draw()
                            current_bank_text.draw()
                            trial_number_text.draw()
                            main_bank_text.draw()
                            win.flip()

                        else:
                            if cfg.bart_burst_sound:
                                sounds["burst"].play()

                            bursted = True

                            trial_info = {
                                "section": "BART",
                                "trial": trial_number,
                                "pumps": blow_num,
                                "gain": 0,
                                "explosion": 1,
                                "RT": time.perf_counter() - last_time,
                            }
                            results.append(trial_info)

                elif keys.getState(cfg.controls["collect"]) and return_status == "UP":
                    space_status = "UP"
                    return_status = "DOWN"

                elif keys.getState(cfg.controls["skip"]):
                    space_status = "UP"
                    break_break = True

                else:
                    space_status = "UP"

                if space_status == "UP":
                    space_counter = 0

                if (
                    not bursted
                    and not break_break
                    and not keys.getState(cfg.controls["collect"])
                    and return_status == "DOWN"
                ):
                    return_status = "UP"
                    if cfg.bart_collect_sound:
                        sounds["collect"].play()

                    collected = True

                    trial_info = {
                        "section": "BART",
                        "trial": trial_number,
                        "pumps": blow_num,
                        "gain": current_liquidity,
                        "explosion": 0,
                        "RT": time.perf_counter() - last_time,
                    }
                    results.append(trial_info)

            if collected:
                main_liquidity += current_liquidity
                main_bank_text.text = catalog.text("bank_balance", amount=main_liquidity)

            trial_number += 1

        total_liquidity += main_liquidity


def make_rating_row(catalog, y, size, spacing):
    """Use catalog-selected numeral images or native text buttons, with equal hit areas."""
    targets, labels = [], []
    for number in range(1, 10):
        pos = [(number - 5) * spacing, y]
        if catalog.rating_image_pattern:
            setting = catalog.rating_image_pattern.format(number=number, state="unselected")
            target = visual.ImageStim(win, image=getattr(cfg, setting), size=size, pos=pos)
        else:
            target = visual.Rect(
                win=win,
                width=size[0],
                height=size[1],
                pos=pos,
                fillColor=catalog.rating_colors["unselected"],
                lineColor=catalog.rating_colors["unselected"],
            )
            labels.append(
                visual.TextStim(
                    win=win,
                    text=str(number),
                    pos=pos,
                    height=size[1] * 0.7,
                    color=cfg.font_color,
                    bold=True,
                    **catalog.text_options,
                )
            )
        targets.append(target)
    return targets, labels


def update_rating_selection(catalog, targets, selected):
    """Highlight the selected value without changing its ordinal or click target."""
    for number, target in enumerate(targets, 1):
        state = "selected" if number == selected else "unselected"
        if catalog.rating_image_pattern:
            setting = catalog.rating_image_pattern.format(number=number, state=state)
            target.image = getattr(cfg, setting)
        else:
            target.fillColor = catalog.rating_colors[state]
            target.lineColor = catalog.rating_colors[state]


def survey(section, catalog):
    first_survey_text = visual.TextStim(
        win=win,
        text=catalog.text("survey_instructions"),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        anchorVert="top",
        pos=[0, (h / 2) - (distance_from_horizontal_edges / 3)],
    )

    press_space_to_proceed = visual.TextStim(
        win=win,
        text=catalog.text("continue", advance_key=cfg.controls["advance"].upper()),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        anchorVert="bottom",
        pos=[0, (-h / 2) + (distance_from_horizontal_edges / 3)],
    )

    sam_width = 2 * w / 20
    sam_height = sam_width
    sam_size = [sam_width, sam_height]
    sam_distance_between = w / 20
    sam_distance_from_vertical_edges = 3 * w / 20

    arousal_height = h / 9

    arousal_1_pos = [-(2 * sam_width + 2 * sam_distance_between), arousal_height]
    arousal_2_pos = [-(1 * sam_width + 1 * sam_distance_between), arousal_height]
    arousal_3_pos = [0, arousal_height]
    arousal_4_pos = [+(1 * sam_width + 1 * sam_distance_between), arousal_height]
    arousal_5_pos = [+(2 * sam_width + 2 * sam_distance_between), arousal_height]

    arousal_1 = visual.ImageStim(win, image=cfg.arousal_1_path, size=sam_size, pos=arousal_1_pos)
    arousal_2 = visual.ImageStim(win, image=cfg.arousal_2_path, size=sam_size, pos=arousal_2_pos)
    arousal_3 = visual.ImageStim(win, image=cfg.arousal_3_path, size=sam_size, pos=arousal_3_pos)
    arousal_4 = visual.ImageStim(win, image=cfg.arousal_4_path, size=sam_size, pos=arousal_4_pos)
    arousal_5 = visual.ImageStim(win, image=cfg.arousal_5_path, size=sam_size, pos=arousal_5_pos)

    least_arousal = visual.TextStim(
        win=win,
        text=catalog.text("arousal_low"),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        anchorVert="bottom",
        pos=[-(w / 2 - sam_distance_from_vertical_edges / 2), arousal_height],
    )

    most_arousal = visual.TextStim(
        win=win,
        text=catalog.text("arousal_high"),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        pos=[+(w / 2 - sam_distance_from_vertical_edges / 2), arousal_height],
    )

    number_size = [w / 30, w / 30]
    arousal_number_height = arousal_height - sam_height / 2 - 0.7 * number_size[1]

    arousal_numbers, arousal_labels = make_rating_row(
        catalog, arousal_number_height, number_size, (sam_width + sam_distance_between) / 2
    )

    pleasure_height = -h / 5

    pleasure_1_pos = [-(2 * sam_width + 2 * sam_distance_between), pleasure_height]
    pleasure_2_pos = [-(1 * sam_width + 1 * sam_distance_between), pleasure_height]
    pleasure_3_pos = [0, pleasure_height]
    pleasure_4_pos = [+(1 * sam_width + 1 * sam_distance_between), pleasure_height]
    pleasure_5_pos = [+(2 * sam_width + 2 * sam_distance_between), pleasure_height]

    pleasure_1 = visual.ImageStim(win, image=cfg.pleasure_1_path, size=sam_size, pos=pleasure_1_pos)
    pleasure_2 = visual.ImageStim(win, image=cfg.pleasure_2_path, size=sam_size, pos=pleasure_2_pos)
    pleasure_3 = visual.ImageStim(win, image=cfg.pleasure_3_path, size=sam_size, pos=pleasure_3_pos)
    pleasure_4 = visual.ImageStim(win, image=cfg.pleasure_4_path, size=sam_size, pos=pleasure_4_pos)
    pleasure_5 = visual.ImageStim(win, image=cfg.pleasure_5_path, size=sam_size, pos=pleasure_5_pos)

    least_pleasure = visual.TextStim(
        win=win,
        text=catalog.text("pleasure_high"),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        pos=[+(w / 2 - sam_distance_from_vertical_edges / 2), pleasure_height],
    )

    most_pleasure = visual.TextStim(
        win=win,
        text=catalog.text("pleasure_low"),
        color=cfg.font_color,
        **catalog.text_options,
        height=font_size,
        bold=True,
        wrapWidth=w,
        pos=[-(w / 2 - sam_distance_from_vertical_edges / 2), pleasure_height],
    )

    pleasure_number_height = pleasure_height - sam_height / 2 - 0.7 * number_size[1]

    pleasure_numbers, pleasure_labels = make_rating_row(
        catalog, pleasure_number_height, number_size, (sam_width + sam_distance_between) / 2
    )

    def draw_survey():
        first_survey_text.draw()
        press_space_to_proceed.draw()
        for stimulus in (
            arousal_1,
            arousal_2,
            arousal_3,
            arousal_4,
            arousal_5,
            pleasure_1,
            pleasure_2,
            pleasure_3,
            pleasure_4,
            pleasure_5,
            most_arousal,
            least_arousal,
            most_pleasure,
            least_pleasure,
            *arousal_numbers,
            *pleasure_numbers,
            *arousal_labels,
            *pleasure_labels,
        ):
            stimulus.draw()

    space_status = "UP"
    mouse_status = "UP"
    proceed = False
    selected_arousal_condition = None
    selected_pleasure_condition = None

    while not proceed:
        check_abort()
        draw_survey()

        buttons = myMouse.getPressed(getTime=False)

        if mouse_status == "UP" and buttons[0] == 1:
            mouse_status = "DOWN"

            for i, stimulus in enumerate(arousal_numbers, 1):
                if myMouse.isPressedIn(stimulus):
                    selected_arousal_condition = i
            for i, stimulus in enumerate(pleasure_numbers, 1):
                if myMouse.isPressedIn(stimulus):
                    selected_pleasure_condition = i

        if mouse_status == "DOWN" and buttons[0] == 0:
            mouse_status = "UP"
            update_rating_selection(catalog, arousal_numbers, selected_arousal_condition)
            update_rating_selection(catalog, pleasure_numbers, selected_pleasure_condition)

        if keys.getState(cfg.controls["advance"]):
            space_status = "DOWN"

        if not keys.getState(cfg.controls["advance"]) and space_status == "DOWN":
            space_status = "UP"
            if selected_arousal_condition is not None and selected_pleasure_condition is not None:
                proceed = True

        win.flip()

    survey_info = {
        "arousal": selected_arousal_condition,
        "pleasure": selected_pleasure_condition,
        "section": section,
    }
    results.append(survey_info)


def run(*, catalog=None):
    """Run one participant session and save partial results on every exit."""
    global visual, event, core, sound, keys, win, results
    global w, h, total_liquidity, font_size
    global distance_from_vertical_edges, distance_from_horizontal_edges, myMouse
    # Importing this module must not open a dialog or require desktop dependencies.
    from psychopy import visual, event, gui, core, sound
    from psychopy.hardware.keyboard import Keyboard

    catalog = load_catalog(cfg.language) if catalog is None else catalog
    catalog.validate()
    prepare_config(cfg, needs_number_images=catalog.rating_image_pattern is not None)
    input_gui = gui.Dlg(title=catalog.text("app_title"))
    for field in PARTICIPANT_FIELDS:
        options = PARTICIPANT_CHOICES.get(field)
        if options:
            input_gui.addField(
                catalog.text(f"field.{field}"),
                choices=[catalog.text(f"choice.{value}") for value in options],
            )
        else:
            input_gui.addField(catalog.text(f"field.{field}"))
    input_gui.show()
    if not input_gui.OK:
        return

    results = SessionResults(cfg.output_directory, cfg.column_order)
    win = None
    mov = None
    try:
        metadata = dict(zip(PARTICIPANT_FIELDS, input_gui.data))
        # Localize the dialog while keeping stored categorical values compatible.
        for field, values in PARTICIPANT_CHOICES.items():
            labels = [catalog.text(f"choice.{value}") for value in values]
            metadata[field] = values[labels.index(metadata[field])]
        results.append(dict(metadata, video=cfg.video_name))
        reset_decks()
        keys = Keyboard()
        win = visual.Window(
            fullscr=cfg.fullscreen, color=cfg.igt_bg_color, units="pix", size=[1200, 675]
        )
        w, h = win.size
        total_liquidity = 0
        font_size = w * 0.0175 + 0.371
        distance_from_vertical_edges = w / 13
        distance_from_horizontal_edges = 1.2 * distance_from_vertical_edges
        myMouse = event.Mouse(win=win)
        fixation = visual.TextStim(
            win=win,
            text=catalog.text("fixation"),
            color=cfg.font_color,
            height=h,
            bold=True,
            wrapWidth=w,
            pos=[0, h / 30],
        )
        fixation.draw()
        win.flip()
        core.wait(cfg.fixation_sleep_time)
        survey(section="before video", catalog=catalog)
        mov = visual.VlcMovieStim(
            win,
            cfg.video_path,
            size=[w, h],
            flipVert=False,
            flipHoriz=False,
            loop=False,
            autoStart=True,
        )
        while not mov.isFinished:
            check_abort()
            movie_keys = event.getKeys(
                keyList=[cfg.controls[key] for key in ("skip", "replay", "pause")]
            )
            if cfg.controls["skip"] in movie_keys:
                break
            if cfg.controls["replay"] in movie_keys:
                mov.replay()
            if cfg.controls["pause"] in movie_keys:
                if mov.isNotStarted or mov.isPaused:
                    mov.play()
                elif mov.isPlaying:
                    mov.pause()
            mov.draw()
            win.flip()
        mov.stop()
        survey(section="after video", catalog=catalog)
        for task in task_order(input_gui.data[1]):
            if task == "IGT":
                igt_experiment(catalog)
            else:
                bart_experiment(catalog)

        text = visual.TextStim(
            win=win,
            text=catalog.text(
                "completion",
                amount=total_liquidity,
                toman=int(total_liquidity * cfg.dollar_toman),
                advance_key=cfg.controls["advance"].upper(),
            ),
            pos=[0, 0],
            color=cfg.bart_font_color,
            **catalog.text_options,
            height=font_size,
            bold=True,
            wrapWidth=w,
        )
        text.draw()
        win.flip()
        wait_for_advance()
    except ExperimentAborted:
        logging.info("Session stopped by operator; completed responses retained.")
    finally:
        # Cleanup failures must not prevent result export, or mask task exceptions.
        try:
            if mov is not None:
                try:
                    mov.stop()
                except Exception:
                    logging.exception("Could not stop video")
            if win is not None:
                try:
                    win.close()
                except Exception:
                    logging.exception("Could not close experiment window")
        finally:
            try:
                results.save()
            finally:
                results.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    run()
