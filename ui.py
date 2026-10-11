"""Native PsychoPy presentation; theme and language are supplied by the caller."""


def rgb(hex_color):
    """Convert theme hex colors to PsychoPy's normalized RGB space."""
    return [int(hex_color[i : i + 2], 16) / 127.5 - 1 for i in (1, 3, 5)]


class TaskScreen:
    def __init__(self, visual, win, catalog, theme):
        self.visual, self.win, self.catalog = visual, win, catalog
        self.w, self.h = win.size
        self.colors = {key: rgb(value) for key, value in theme.items()}

    def text(self, message, pos, *, size=20, color="ink", bold=False, width=None, **kwargs):
        return self.visual.TextStim(
            self.win,
            text=message,
            pos=pos,
            height=size * self.w / 1200,
            color=self.colors[color],
            bold=bold,
            wrapWidth=width or self.w * 0.8,
            **self.catalog.text_options,
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


class IgtScreen(TaskScreen):
    """Four equivalent deck targets; outcomes remain on the selected card."""

    def __init__(self, visual, win, catalog, theme):
        super().__init__(visual, win, catalog, theme)
        width, height = self.w * 0.18, self.h * 0.44
        self.cards, self.labels, self.numbers, self.hints = [], [], [], []
        self.gains, self.losses, self.feedback_labels = [], [], []
        for number in range(1, 5):
            x, y = (number - 2.5) * self.w * 0.225, -self.h * 0.045
            self.cards.append(self.rect((x, y), width, height, fill="deck"))
            self.labels.append(
                self.text(
                    catalog.text("deck", number=number),
                    (x, y + height * 0.38),
                    size=21,
                    bold=True,
                    width=width * 0.9,
                )
            )
            self.numbers.append(
                self.text(str(number), (x, y), size=56, color="accent", bold=True, width=width)
            )
            self.hints.append(
                self.text(
                    catalog.text("igt_pick"),
                    (x, y - height * 0.37),
                    size=17,
                    color="muted",
                    width=width * 0.9,
                )
            )
            self.feedback_labels.append(
                (
                    self.text(
                        catalog.text("igt_gain_label"),
                        (x, y + height * 0.18),
                        size=17,
                        color="muted",
                        width=width * 0.9,
                    ),
                    self.text(
                        catalog.text("igt_loss_label"),
                        (x, y - height * 0.16),
                        size=17,
                        color="muted",
                        width=width * 0.9,
                    ),
                )
            )
            self.gains.append(
                self.text(
                    "", (x, y + height * 0.045), size=30, color="gain", bold=True, width=width * 0.9
                )
            )
            self.losses.append(
                self.text(
                    "", (x, y - height * 0.295), size=30, color="loss", bold=True, width=width * 0.9
                )
            )
        direction = -1 if catalog.is_rtl else 1
        self.title = self.text(
            catalog.text("igt_title"),
            (-direction * self.w * 0.425, self.h * 0.39),
            size=28,
            bold=True,
            anchorHoriz="right" if catalog.is_rtl else "left",
            alignText="right" if catalog.is_rtl else "left",
        )
        self.balance = self.text(
            "",
            (direction * self.w * 0.425, self.h * 0.39),
            size=23,
            bold=True,
            anchorHoriz="left" if catalog.is_rtl else "right",
            alignText="left" if catalog.is_rtl else "right",
        )
        self.divider = self.rect((0, self.h * 0.315), self.w * 0.85, 1, fill="border")
        self.prompt = self.text(catalog.text("igt_choose"), (0, self.h * 0.225), size=24)
        self.progress = self.text("", (0, -self.h * 0.4), size=18, color="muted")

    def draw(self, trial, trials, balance, *, selected=None, outcome=None):
        self.balance.text = self.catalog.text("igt_balance_value", amount=balance)
        self.progress.text = self.catalog.text("igt_progress", number=trial, trials=trials)
        self.prompt.text = self.catalog.text("igt_result" if outcome is not None else "igt_choose")
        for stimulus in (self.title, self.balance, self.divider, self.prompt, self.progress):
            stimulus.draw()
        for index, card in enumerate(self.cards):
            revealed = selected == index + 1 and outcome is not None
            card.fillColor = self.colors["surface" if revealed else "deck"]
            card.lineColor = self.colors["accent" if revealed else "border"]
            card.lineWidth = 3 if revealed else 1
            card.draw()
            self.labels[index].draw()
            if revealed:
                gain, loss = outcome
                self.gains[index].color = self.colors["gain" if gain else "muted"]
                self.losses[index].color = self.colors["loss" if loss else "muted"]
                self.gains[index].text = self.catalog.text("igt_gain_amount", amount=gain)
                self.losses[index].text = self.catalog.text("igt_loss_amount", amount=loss)
                for stimulus in (
                    *self.feedback_labels[index],
                    self.gains[index],
                    self.losses[index],
                ):
                    stimulus.draw()
            else:
                self.numbers[index].draw()
                self.hints[index].draw()
