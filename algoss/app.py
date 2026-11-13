import random
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input, Label, Select

from .algorithms import (
    DEFAULT_COINS,
    DEFAULT_SEARCH,
    DEFAULT_SORT,
    bubble,
    selection,
    insertion,
    quicksort,
    mergesort,
    shaker,
    binary_search,
    linear_search,
    coin_change,
)
from .views import Canvas, SpeedBar, StateCard, TraceView

CATEGORIES = {
    "Сортировки": [
        "Пузырьковая",
        "Выбором",
        "Вставками",
        "Быстрая (Quick)",
        "Слиянием (Merge)",
        "Шейкерная (Cocktail)",
    ],
    "Поиск": [
        "Бинарный поиск",
        "Линейный поиск",
    ],
    "Жадные": [
        "Размен монет",
    ],
}


def parse_ints(raw: str, default: list[int]) -> list[int]:
    try:
        nums = [int(x) for x in raw.replace(",", " ").split() if x.strip()]
        return nums if nums else default
    except ValueError:
        return default


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
        self.timer = None
        self.playing = False
        self.steps = 0

    def compose(self) -> ComposeResult:
        first_cat = next(iter(CATEGORIES))
        first_algos = CATEGORIES[first_cat]
        with Horizontal(id="body"):
            with Vertical(id="side"):
                yield Label("┌─ КАТЕГОРИЯ", classes="cap")
                yield Select(
                    [(c, c) for c in CATEGORIES],
                    value=first_cat,
                    allow_blank=False,
                    id="cat",
                )
                yield Label("┌─ АЛГОРИТМ", classes="cap")
                yield Select(
                    [(n, n) for n in first_algos],
                    value=first_algos[0],
                    allow_blank=False,
                    id="algo",
                )

                yield Label("┌─ ПАРАМЕТР 1", id="lbl_p1", classes="cap")
                yield Input(", ".join(map(str, DEFAULT_SORT)), id="p1")

                yield Label("┌─ ПАРАМЕТР 2", id="lbl_p2", classes="cap")
                yield Input("23", id="p2")

                with Horizontal(id="param_buttons"):
                    yield Button("🎲 Случайно", id="btn_rand")
                    yield Button("↵ Применить", id="btn_apply")

                yield Label("┌─ УПРАВЛЕНИЕ", classes="cap")
                yield Button("▶ Старт", id="play", variant="primary")
                yield Button("⏭ Шаг", id="step")
                yield Button("↺ Сброс", id="reset")

                yield Label("┌─ СКОРОСТЬ", classes="cap")
                yield SpeedBar(50, id="speed")

            with Vertical(id="main"):
                yield Canvas(id="canvas")
                yield StateCard(id="state")
                yield TraceView(id="trace")
        yield Footer()

    def on_mount(self):
        for btn in self.query(Button):
            btn.FOCUS_ON_CLICK = False
        self.update_param_visibility()
        self.load()

    def update_param_visibility(self):
        cat = self.query_one("#cat", Select).value
        lbl_p1 = self.query_one("#lbl_p1", Label)
        inp_p1 = self.query_one("#p1", Input)
        lbl_p2 = self.query_one("#lbl_p2", Label)
        inp_p2 = self.query_one("#p2", Input)
        btn_rand = self.query_one("#btn_rand", Button)

        if cat == "Сортировки":
            lbl_p1.update("┌─ МАССИВ ДЛЯ СОРТИРОВКИ")
            lbl_p2.display = False
            inp_p2.display = False
            btn_rand.display = True
        elif cat == "Поиск":
            lbl_p1.update("┌─ МАССИВ ЧИСЕЛ")
            lbl_p2.update("┌─ ИСКОМОЕ ЧИСЛО")
            lbl_p2.display = True
            inp_p2.display = True
            btn_rand.display = True
        else:
            lbl_p1.update("┌─ СУММА ДЛЯ РАЗМЕНА")
            lbl_p2.update("┌─ НОМИНАЛЫ МОНЕТ")
            lbl_p2.display = True
            inp_p2.display = True
            btn_rand.display = True

    def build_generator(self):
        cat = self.query_one("#cat", Select).value
        name = self.query_one("#algo", Select).value
        p1 = self.query_one("#p1", Input).value
        p2 = self.query_one("#p2", Input).value

        if cat == "Сортировки":
            arr = parse_ints(p1, DEFAULT_SORT)
            if name == "Пузырьковая":
                return bubble(arr)
            elif name == "Выбором":
                return selection(arr)
            elif name == "Вставками":
                return insertion(arr)
            elif name == "Быстрая (Quick)":
                return quicksort(arr)
            elif name == "Слиянием (Merge)":
                return mergesort(arr)
            elif name == "Шейкерная (Cocktail)":
                return shaker(arr)
        elif cat == "Поиск":
            arr = parse_ints(p1, DEFAULT_SEARCH)
            target = parse_ints(p2, [23])[0]
            if name == "Бинарный поиск":
                return binary_search(arr, target)
            elif name == "Линейный поиск":
                return linear_search(arr, target)
        elif cat == "Жадные":
            amount = parse_ints(p1, [137])[0]
            coins = parse_ints(p2, DEFAULT_COINS)
            return coin_change(amount, coins)

        return bubble(DEFAULT_SORT)

    def load(self):
        self.stop_playing()
        self.gen = self.build_generator()
        self.steps = 0
        self.query_one(TraceView).clear()
        self.query_one(Canvas).show(None)
        self.query_one(StateCard).update_state(None, 0)
        self.advance()
        self.set_focus(None)

    def advance(self):
        if self.gen is None:
            return
        try:
            step = next(self.gen)
        except StopIteration:
            self.gen = None
            self.stop_playing()
            return
        self.steps += 1
        self.query_one(Canvas).show(step)
        self.query_one(StateCard).update_state(step, self.steps)
        self.query_one(TraceView).add(self.steps, step.message)

    def delay(self):
        value = self.query_one(SpeedBar).value
        return 0.02 + (100 - value) * 0.008

    def set_playing(self, playing: bool):
        self.playing = playing
        btn = self.query_one("#play", Button)
        btn.label = "⏸ Пауза" if playing else "▶ Старт"
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
            cat = event.value
            names = CATEGORIES[cat]
            algo = self.query_one("#algo", Select)
            algo.set_options([(n, n) for n in names])
            algo.value = names[0]
            if cat == "Сортировки":
                self.query_one("#p1", Input).value = ", ".join(map(str, DEFAULT_SORT))
            elif cat == "Поиск":
                self.query_one("#p1", Input).value = ", ".join(map(str, DEFAULT_SEARCH))
                self.query_one("#p2", Input).value = "23"
            else:
                self.query_one("#p1", Input).value = "137"
                self.query_one("#p2", Input).value = ", ".join(map(str, DEFAULT_COINS))
            self.update_param_visibility()
        self.load()

    def on_button_pressed(self, event):
        btn_id = event.button.id
        if btn_id == "play":
            self.action_toggle()
        elif btn_id == "step":
            self.action_step()
        elif btn_id == "reset" or btn_id == "btn_apply":
            self.action_reset()
        elif btn_id == "btn_rand":
            self.randomize_params()

    def on_input_submitted(self, _):
        self.action_reset()

    def randomize_params(self):
        cat = self.query_one("#cat", Select).value
        if cat == "Сортировки":
            count = random.randint(7, 12)
            vals = [random.randint(1, 30) for _ in range(count)]
            self.query_one("#p1", Input).value = ", ".join(map(str, vals))
        elif cat == "Поиск":
            count = random.randint(8, 12)
            vals = sorted(random.sample(range(1, 60), count))
            target = random.choice(vals) if random.random() < 0.75 else random.randint(1, 60)
            self.query_one("#p1", Input).value = ", ".join(map(str, vals))
            self.query_one("#p2", Input).value = str(target)
        else:
            amount = random.randint(25, 240)
            self.query_one("#p1", Input).value = str(amount)
        self.load()

    def on_speed_bar_changed(self, _):
        if self.playing:
            self.set_playing(True)


def main():
    Algoss().run()


if __name__ == "__main__":
    main()
