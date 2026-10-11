"""Native PsychoPy presentation; theme and language are supplied by the caller."""

import math


def rgb(hex_color):
    """Convert theme hex colors to PsychoPy's normalized RGB space."""
    return [int(hex_color[i : i + 2], 16) / 127.5 - 1 for i in (1, 3, 5)]


class TaskScreen:
    def __init__(self, visual, win, catalog, theme):
        self.visual, self.win, self.catalog = visual, win, catalog
        self.w, self.h = win.size
        self.colors = {key: rgb(value) for key, value in theme.items()}

    def text(
        self, message, pos, *, size=20, color="ink", bold=False, width=None, display=False, **kwargs
    ):
        options = dict(self.catalog.text_options)
        if display and self.catalog.display_font:
            options["font"] = self.catalog.display_font
        return self.visual.TextStim(
            self.win,
            text=message,
            pos=pos,
            height=size * self.w / 1200,
            color=self.colors[color],
            bold=bold,
            wrapWidth=width or self.w * 0.8,
            **options,
            **kwargs,
        )

    def rect(self, pos, width, height, *, fill="surface", border="border", line_width=1):
        return self.visual.Rect(
            self.win,
            pos=pos,
            width=width,
            height=height,
            fillColor=self.colors[fill],
            lineColor=self.colors[border],
            lineWidth=line_width,
        )

    def instructions(self, task, message):
        """Improve hierarchy without changing the study's instruction content."""
        self.text(self.catalog.text(f"{task}_title"), (0, self.h * 0.39), size=32, bold=True).draw()
        self.rect((0, self.h * 0.31), self.w * 0.74, 1, fill="border").draw()
        self.text(message, (0, -self.h * 0.025), size=20, width=self.w * 0.74).draw()

    def shape(self, vertices, pos, size, *, fill=None, border=None, line_width=1, closed=True):
        return self.visual.ShapeStim(
            self.win,
            vertices=vertices,
            pos=pos,
            size=size,
            closeShape=closed,
            fillColor=self.colors[fill] if fill else None,
            lineColor=self.colors[border] if border else None,
            lineWidth=line_width,
        )

    def paper(self, pos, width, height, *, fill="surface", border="border", radius=9):
        vertices = []
        for cx, cy, start in (
            (width / 2 - radius, height / 2 - radius, 0),
            (-width / 2 + radius, height / 2 - radius, 90),
            (-width / 2 + radius, -height / 2 + radius, 180),
            (width / 2 - radius, -height / 2 + radius, 270),
        ):
            for step in range(9):
                angle = math.radians(start + step * 90 / 8)
                vertices.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return self.shape(vertices, pos, (1, 1), fill=fill, border=border)

    def background(self):
        self.rect((0, 0), self.w, self.h, fill="canvas", border="canvas").draw()


class IgtScreen(TaskScreen):
    """Printed, equivalent deck backs; a selected card carries its own receipt."""

    def __init__(self, visual, win, catalog, theme):
        super().__init__(visual, win, catalog, theme)
        self.cards, self.backs, self.fronts, self.labels = [], [], [], []
        self.gains, self.losses, self.outcome_labels = [], [], []
        width, height = self.w * 0.155, self.h * 0.425
        for number in range(1, 5):
            x, y = (number - 2.5) * self.w * 0.198, -self.h * 0.015
            # Actual click targets share the visible front card's bounds.
            self.cards.append(self.rect((x, y), width, height, fill="surface"))
            layers = [
                self.paper((x + 5, y - 10), width, height, fill="shadow", border="shadow"),
                self.paper((x + 3, y - 6), width, height, fill="surface"),
                self.paper((x + 1, y - 3), width, height, fill="surface"),
            ]
            back = self.paper((x, y), width, height, fill="deck", border="deck")
            frame = self.paper(
                (x, y), width - 18, height - 18, fill="deck", border="pattern", radius=5
            )
            ornaments = []
            # Restrained engraved diamonds, identical on every deck.
            for scale in (0.27, 0.42, 0.57, 0.72):
                ornaments.append(
                    self.shape(
                        [(0, 0.5), (0.5, 0), (0, -0.5), (-0.5, 0)],
                        (x, y),
                        (width * scale, height * scale),
                        border="pattern",
                    )
                )
            for sign in (-1, 1):
                ornaments.append(
                    self.shape(
                        [(0, 0.5), (0.5, 0), (0, -0.5), (-0.5, 0)],
                        (x, y + sign * height * 0.37),
                        (11, 14),
                        fill="on_deck",
                    )
                )
            self.backs.append([*layers, back, frame, *ornaments])
            corner = self.text(
                str(number),
                (x - width * 0.34, y + height * 0.38),
                size=19,
                display=True,
                width=width * 0.25,
            )
            opposite = self.text(
                str(number),
                (x + width * 0.34, y - height * 0.38),
                size=19,
                display=True,
                width=width * 0.25,
            )
            divider = self.rect((x, y - height * 0.03), width * 0.69, 1, fill="border")
            front = self.paper((x, y), width, height)
            self.fronts.append([*layers, front, corner, opposite, divider])
            self.labels.append(
                self.text(
                    catalog.text("deck", number=number),
                    (x, y - height * 0.65),
                    size=22,
                    display=True,
                    width=width * 1.1,
                )
            )
            self.outcome_labels.append(
                (
                    self.text(
                        catalog.text("igt_gain_label"),
                        (x, y + height * 0.24),
                        size=16,
                        color="muted",
                        width=width * 0.85,
                    ),
                    self.text(
                        catalog.text("igt_loss_label"),
                        (x, y - height * 0.12),
                        size=16,
                        color="muted",
                        width=width * 0.85,
                    ),
                )
            )
            self.gains.append(
                self.text(
                    "",
                    (x, y + height * 0.11),
                    size=31,
                    display=True,
                    color="gain",
                    width=width * 0.9,
                )
            )
            self.losses.append(
                self.text(
                    "",
                    (x, y - height * 0.25),
                    size=31,
                    display=True,
                    color="loss",
                    width=width * 0.9,
                )
            )
        direction = -1 if catalog.is_rtl else 1
        start, end = "right" if catalog.is_rtl else "left", "left" if catalog.is_rtl else "right"
        self.title = self.text(
            catalog.text("igt_title"),
            (-direction * self.w * 0.41, self.h * 0.365),
            size=34,
            display=True,
            anchorHoriz=start,
            alignText=start,
        )
        self.prompt = self.text(
            "",
            (-direction * self.w * 0.41, self.h * 0.295),
            size=18,
            color="muted",
            anchorHoriz=start,
            alignText=start,
        )
        self.balance_label = self.text(
            catalog.text("igt_balance"),
            (direction * self.w * 0.41, self.h * 0.39),
            size=16,
            color="muted",
            anchorHoriz=end,
            alignText=end,
        )
        self.balance = self.text(
            "",
            (direction * self.w * 0.41, self.h * 0.32),
            size=32,
            display=True,
            anchorHoriz=end,
            alignText=end,
        )
        self.progress = self.text(
            "",
            (-direction * self.w * 0.41, -self.h * 0.405),
            size=17,
            color="muted",
            anchorHoriz=start,
            alignText=start,
        )
        self.rule = self.rect((0, -self.h * 0.355), self.w * 0.82, 1, fill="border")

    def draw(self, trial, trials, balance, *, selected=None, outcome=None):
        self.background()
        self.balance.text = self.catalog.text("igt_amount", amount=balance)
        self.prompt.text = self.catalog.text("igt_result" if outcome is not None else "igt_choose")
        self.progress.text = self.catalog.text("igt_progress", number=trial, trials=trials)
        for stimulus in (
            self.title,
            self.prompt,
            self.balance_label,
            self.balance,
            self.rule,
            self.progress,
        ):
            stimulus.draw()
        for index in range(4):
            revealed = selected == index + 1 and outcome is not None
            for stimulus in self.fronts[index] if revealed else self.backs[index]:
                stimulus.draw()
            self.labels[index].draw()
            if revealed:
                gain, loss = outcome
                self.gains[index].text = self.catalog.text("igt_gain_amount", amount=gain)
                self.losses[index].text = self.catalog.text("igt_loss_amount", amount=loss)
                self.gains[index].color = self.colors["gain" if gain else "muted"]
                self.losses[index].color = self.colors["loss" if loss else "muted"]
                for stimulus in (
                    *self.outcome_labels[index],
                    self.gains[index],
                    self.losses[index],
                ):
                    stimulus.draw()


class BartScreen(TaskScreen):
    """A vector balloon stage and a separate reward ledger, with keyboard legends."""

    def __init__(self, visual, win, catalog, theme, controls, presentation):
        super().__init__(visual, win, catalog, theme)
        self.presentation = presentation
        direction = -1 if catalog.is_rtl else 1
        self.x = -direction * self.w * 0.15
        ledger_x = direction * self.w * 0.30
        self.title = self.text(
            catalog.text("bart_title"),
            (-direction * self.w * 0.41, self.h * 0.365),
            size=34,
            display=True,
            anchorHoriz="right" if catalog.is_rtl else "left",
            alignText="right" if catalog.is_rtl else "left",
        )
        self.trial = self.text(
            "",
            (direction * self.w * 0.41, self.h * 0.365),
            size=18,
            color="muted",
            anchorHoriz="left" if catalog.is_rtl else "right",
        )
        self.rule = self.rect((0, self.h * 0.28), self.w * 0.82, 1, fill="border")
        self.ledger_rule = self.rect((ledger_x, self.h * 0.025), self.w * 0.23, 1, fill="border")
        self.value_label = self.text(
            catalog.text("bart_value_label"),
            (ledger_x, self.h * 0.19),
            size=18,
            color="muted",
            width=self.w * 0.24,
        )
        self.value = self.text(
            "", (ledger_x, self.h * 0.105), size=49, display=True, width=self.w * 0.25
        )
        self.bank_label = self.text(
            catalog.text("bart_bank_label"),
            (ledger_x, -self.h * 0.06),
            size=18,
            color="muted",
            width=self.w * 0.24,
        )
        self.bank = self.text(
            "", (ledger_x, -self.h * 0.13), size=31, display=True, width=self.w * 0.25
        )
        body = [(0, -0.52)]
        for step in range(81):
            angle = -math.pi + 0.19 + step * (2 * math.pi - 0.38) / 80
            body.append(
                (0.5 * math.sin(angle) * (1 + 0.12 * math.cos(angle)), 0.5 * math.cos(angle))
            )
        self.balloon = self.shape(
            body, (self.x, 0), (1, 1), fill="balloon", border="balloon_edge", line_width=1.5
        )
        self.highlight = self.shape(
            [(-0.26, -0.13), (-0.34, 0.02), (-0.30, 0.20), (-0.19, 0.34)],
            (self.x, 0),
            (1, 1),
            border="balloon_light",
            line_width=4,
            closed=False,
        )
        self.knot = self.shape(
            [(-0.04, -0.59), (0, -0.52), (0.04, -0.59)], (self.x, 0), (1, 1), fill="balloon_edge"
        )
        self.string = self.shape([(0, 0), (0, 1)], (0, 0), (1, 1), border="muted", closed=False)
        ellipse = [
            (math.cos(i * math.pi / 24) * 0.5, math.sin(i * math.pi / 24) * 0.5) for i in range(48)
        ]
        self.shadow = self.shape(
            ellipse, (self.x, -self.h * 0.32), (self.w * 0.14, self.h * 0.016), fill="shadow"
        )
        self.legends = []
        for offset, action, label in (
            (-0.17, "pump", "bart_pump"),
            (0.17, "collect", "bart_collect"),
        ):
            x = self.w * offset
            key = controls[action].upper()
            self.legends.extend(
                [
                    self.paper(
                        (x - self.w * 0.045, -self.h * 0.415),
                        self.w * 0.09,
                        self.h * 0.043,
                        radius=4,
                    ),
                    self.text(
                        key, (x - self.w * 0.045, -self.h * 0.415), size=14, width=self.w * 0.087
                    ),
                    self.text(
                        catalog.text(label),
                        (x + self.w * 0.025, -self.h * 0.415),
                        size=18,
                        width=self.w * 0.10,
                    ),
                ]
            )

    def draw(self, trial, trials, value, bank, pumps, capacity):
        self.background()
        self.trial.text = self.catalog.text("bart_progress", number=trial, trials=trials)
        self.value.text = self.catalog.text("igt_amount", amount=value)
        self.bank.text = self.catalog.text("igt_amount", amount=bank)
        fraction = min(pumps / capacity, 1)
        width = self.w * (
            self.presentation["min_width"]
            + fraction * (self.presentation["max_width"] - self.presentation["min_width"])
        )
        height = self.h * (
            self.presentation["min_height"]
            + fraction * (self.presentation["max_height"] - self.presentation["min_height"])
        )
        y = self.h * self.presentation["center_y"]
        for stimulus in (self.balloon, self.highlight, self.knot):
            stimulus.size = (width, height)
            stimulus.pos = (self.x, y)
        bottom = y - height * 0.59
        end = min(-self.h * 0.30, bottom - self.h * 0.03)
        self.string.vertices = [
            (
                self.x + math.sin(t * math.pi * 2) * self.w * 0.007 * (1 - t),
                bottom + (end - bottom) * t,
            )
            for t in [i / 30 for i in range(31)]
        ]
        self.shadow.draw()
        self.string.draw()
        self.balloon.draw()
        self.highlight.draw()
        self.knot.draw()
        for stimulus in (
            self.title,
            self.trial,
            self.rule,
            self.ledger_rule,
            self.value_label,
            self.value,
            self.bank_label,
            self.bank,
            *self.legends,
        ):
            stimulus.draw()
