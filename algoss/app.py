from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Label, Select, Static

from .algorithms import PROGRAMS
from .views import Canvas, SpeedBar


class Algoss(App):
    CSS_PATH = "app.tcss"
    TITLE = "algoss"
    BINDINGS = [
        ("space", "toggle", "старт/пауза"),
        ("right", "step", "шаг"),
        ("r", "reset", "сброс"),
        ("q", "quit", "выход"),
    ]

    def __init__(self):
        super().__init__()
        self.gen = None
        self.code: list[str] = []
        self.timer = None
        self.playing = False

    def compose(self) -> ComposeResult:
        category = next(iter(PROGRAMS))
        names = list(PROGRAMS[category])
        with Horizontal(id="body"):
            with Vertical(id="side"):
                yield Label("категория", classes="cap")
                yield Select(
                    [(c, c) for c in PROGRAMS],
                    value=category,
                    allow_blank=False,
                    id="cat",
                )
                yield Label("алгоритм", classes="cap")
                yield Select(
                    [(n, n) for n in names],
                    value=names[0],
                    allow_blank=False,
                    id="algo",
                )
                yield Label("управление", classes="cap")
                yield Button("старт", id="play", variant="primary")
                yield Button("шаг", id="step")
                yield Button("сброс", id="reset")
                yield Label("скорость", classes="cap")
                yield SpeedBar(50, id="speed")
            with Vertical(id="main"):
                yield Canvas(id="canvas")
                yield Static(id="info")
        yield Footer()

    def on_mount(self):
        for button in self.query(Button):
            button.focus_on_click = False
        self.load()

    def load(self):
        self.stop_playing()
        category = self.query_one("#cat", Select).value
        name = self.query_one("#algo", Select).value
        program = PROGRAMS[category][name]
        self.gen = program.run()
        self.code = program.code
        self.query_one("#info", Static).update("")
        self.query_one(Canvas).show(None)
        self.advance()

    def advance(self):
        if self.gen is None:
            return
        try:
            step = next(self.gen)
        except StopIteration:
            self.gen = None
            self.stop_playing()
            return
        self.query_one(Canvas).show(step, self.code)
        info = Text(step.message, style="bold")
        if step.vars:
            line = "   ".join(f"{k}={v}" for k, v in step.vars.items())
            info.append(f"\n{line}", style="grey62")
        self.query_one("#info", Static).update(info)

    def delay(self):
        value = self.query_one(SpeedBar).value
        return 0.02 + (100 - value) * 0.008

    def set_playing(self, playing: bool):
        self.playing = playing
        self.query_one("#play", Button).label = "пауза" if playing else "старт"
        if self.timer:
            self.timer.stop()
            self.timer = None
        if playing:
            self.timer = self.set_interval(self.delay(), self.advance)

    def stop_playing(self):
        self.set_playing(False)

    def action_toggle(self):
        if self.gen is None:
            self.load()
        self.set_playing(not self.playing)

    def action_step(self):
        self.stop_playing()
        self.advance()

    def action_reset(self):
        self.load()

    def on_select_changed(self, event):
        if event.select.id == "cat":
            names = list(PROGRAMS[event.value])
            algo = self.query_one("#algo", Select)
            algo.set_options([(n, n) for n in names])
            algo.value = names[0]
        else:
            self.load()

    def on_button_pressed(self, event):
        if event.button.id == "play":
            self.action_toggle()
        elif event.button.id == "step":
            self.action_step()
        else:
            self.action_reset()

    def on_speed_bar_changed(self, event):
        if self.playing:
            self.set_playing(True)


def main():
    Algoss().run()


if __name__ == "__main__":
    main()
