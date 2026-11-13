import random
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label

from .algorithms import (
    DEFAULT_COINS,
    DEFAULT_PREFIX,
    DEFAULT_SEARCH,
    DEFAULT_SORT,
    DEFAULT_TWO_POINTERS,
    binary_search,
    bubble,
    coin_change,
    insertion,
    linear_search,
    prefix_sums,
    selection,
    two_pointers,
)
from .views import (
    AlgoList,
    Canvas,
    CategoryBar,
    LogoView,
    StateCard,
    TraceView,
    VimKeymap,
    VimStatusBar,
)

CATEGORIES = {
    "Сортировки": [
        "Пузырьковая",
        "Выбором",
        "Вставками",
    ],
    "Массивы": [
        "Два указателя",
        "Префиксные суммы",
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
    AUTO_FOCUS = None
    BINDINGS = [
        ("space", "toggle", "старт/пауза"),
        ("left", "handle_left", "назад / пред. режим"),
        ("right", "handle_right", "вперед / след. режим"),
        ("n", "step_forward", "шаг вперед"),
        ("p", "step_backward", "шаг назад"),
        ("r", "reset", "сброс"),
        ("j", "next_algo", "след. алгоритм"),
        ("down", "next_algo", "след. алгоритм"),
        ("k", "prev_algo", "пред. алгоритм"),
        ("up", "prev_algo", "пред. алгоритм"),
        ("h", "prev_cat", "пред. режим"),
        ("l", "next_cat", "след. режим"),
        ("1", "cat_1", "режим 1"),
        ("2", "cat_2", "режим 2"),
        ("3", "cat_3", "режим 3"),
        ("4", "cat_4", "режим 4"),
        ("i", "edit", "редактировать"),
        ("e", "edit", "редактировать"),
        ("g", "rand", "случайные"),
        ("minus", "slower", "медленнее"),
        ("underscore", "slower", "медленнее"),
        ("plus", "faster", "быстрее"),
        ("equals", "faster", "быстрее"),
        ("escape", "cancel_edit", "отмена"),
        ("q", "quit", "выход"),
    ]

    def __init__(self):
        super().__init__()
        self.gen = None
        self.timer = None
        self.playing = False
        self.steps = 0
        self.speed = 50
        self.mode = "NORMAL"

        self.history = []
        self.history_idx = -1

        self.current_cat = "Сортировки"
        self.current_algo = "Пузырьковая"

        self.p1_sort = ", ".join(map(str, DEFAULT_SORT))
        self.p1_arrays = ", ".join(map(str, DEFAULT_TWO_POINTERS))
        self.p2_arrays = "26"
        self.p1_search = ", ".join(map(str, DEFAULT_SEARCH))
        self.p2_search = "23"
        self.p1_greedy = "137"
        self.p2_greedy = ", ".join(map(str, DEFAULT_COINS))

    @property
    def current_p1(self) -> str:
        if self.current_cat == "Сортировки":
            return self.p1_sort
        elif self.current_cat == "Массивы":
            return self.p1_arrays
        elif self.current_cat == "Поиск":
            return self.p1_search
        return self.p1_greedy

    @current_p1.setter
    def current_p1(self, val: str):
        if self.current_cat == "Сортировки":
            self.p1_sort = val
        elif self.current_cat == "Массивы":
            self.p1_arrays = val
        elif self.current_cat == "Поиск":
            self.p1_search = val
        else:
            self.p1_greedy = val

    @property
    def current_p2(self) -> str:
        if self.current_cat == "Массивы":
            return self.p2_arrays
        elif self.current_cat == "Поиск":
            return self.p2_search
        return self.p2_greedy

    @current_p2.setter
    def current_p2(self, val: str):
        if self.current_cat == "Массивы":
            self.p2_arrays = val
        elif self.current_cat == "Поиск":
            self.p2_search = val
        else:
            self.p2_greedy = val

    def compose(self) -> ComposeResult:
        with Horizontal(id="body"):
            with Vertical(id="side"):
                yield LogoView(current_cat=self.current_cat, id="logo")
                yield CategoryBar(list(CATEGORIES.keys()), self.current_cat, id="cat_bar")
                yield AlgoList(CATEGORIES[self.current_cat], self.current_algo, id="algo_list")
                yield VimKeymap(self.speed, self.playing, id="keymap")

            with Vertical(id="main"):
                yield Canvas(id="canvas")

                with Horizontal(id="numbers_box"):
                    yield Label("Массив:", id="lbl_p1", classes="cfg_lbl")
                    yield Input(self.current_p1, id="input_p1", classes="cfg_inp")
                    yield Label("Искать:", id="lbl_p2", classes="cfg_lbl hidden")
                    yield Input(self.current_p2, id="input_p2", classes="cfg_inp_sm hidden")
                    yield Button("🎲 Rand", id="btn_rand", classes="cfg_btn")
                    yield Button("↵ Применить", id="btn_apply", classes="cfg_btn")

                yield StateCard(id="state")
                yield TraceView(id="trace")

        yield VimStatusBar(id="status_bar")

    def on_mount(self):
        for btn in self.query(Button):
            btn.FOCUS_ON_CLICK = False
        box = self.query_one("#numbers_box")
        box.border_title = " НАСТРОЙКА ЧИСЕЛ [i: фокус, g: rand, Enter: применить] "
        self.update_numbers_ui()
        self.set_focus(None)
        self.load()

    def update_numbers_ui(self):
        lbl_p1 = self.query_one("#lbl_p1", Label)
        inp_p1 = self.query_one("#input_p1", Input)
        lbl_p2 = self.query_one("#lbl_p2", Label)
        inp_p2 = self.query_one("#input_p2", Input)

        if self.current_cat == "Сортировки":
            lbl_p1.update("Массив:")
            inp_p1.value = self.p1_sort
            lbl_p2.display = False
            inp_p2.display = False
        elif self.current_cat == "Массивы":
            if self.current_algo == "Два указателя":
                lbl_p1.update("Массив:")
                inp_p1.value = self.p1_arrays
                lbl_p2.update("Цель:")
                inp_p2.value = self.p2_arrays
            else:
                lbl_p1.update("Массив:")
                inp_p1.value = self.p1_arrays
                lbl_p2.update("Отрезок:")
                inp_p2.value = self.p2_arrays
            lbl_p2.display = True
            inp_p2.display = True
        elif self.current_cat == "Поиск":
            lbl_p1.update("Массив:")
            inp_p1.value = self.p1_search
            lbl_p2.update("Искать:")
            inp_p2.value = self.p2_search
            lbl_p2.display = True
            inp_p2.display = True
        else:
            lbl_p1.update("Сумма:")
            inp_p1.value = self.p1_greedy
            lbl_p2.update("Монеты:")
            inp_p2.value = self.p2_greedy
            lbl_p2.display = True
            inp_p2.display = True

    def set_category(self, cat: str):
        if cat not in CATEGORIES or cat == self.current_cat:
            return
        self.current_cat = cat
        self.query_one(LogoView).set_category(cat)
        self.query_one(CategoryBar).current = cat
        self.query_one(CategoryBar).refresh()

        algos = CATEGORIES[cat]
        self.current_algo = algos[0]
        self.query_one(AlgoList).set_items(algos, self.current_algo)
        self.update_numbers_ui()
        self.load()

    def set_algorithm(self, name: str):
        if name in CATEGORIES[self.current_cat] and name != self.current_algo:
            self.current_algo = name
            self.query_one(AlgoList).current = name
            self.query_one(AlgoList).refresh()
            self.update_numbers_ui()
            self.load()

    def build_generator(self):
        cat = self.current_cat
        name = self.current_algo
        p1 = self.current_p1
        p2 = self.current_p2

        if cat == "Сортировки":
            arr = parse_ints(p1, DEFAULT_SORT)
            if name == "Пузырьковая":
                return bubble(arr)
            elif name == "Выбором":
                return selection(arr)
            elif name == "Вставками":
                return insertion(arr)
        elif cat == "Массивы":
            if name == "Два указателя":
                arr = parse_ints(p1, DEFAULT_TWO_POINTERS)
                target = parse_ints(p2, [26])[0]
                return two_pointers(arr, target)
            elif name == "Префиксные суммы":
                arr = parse_ints(p1, DEFAULT_PREFIX)
                return prefix_sums(arr, p2)
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
        self.history = []
        self.history_idx = -1
        self.steps = 0
        self.query_one(TraceView).clear()
        self.query_one(Canvas).show(None)
        self.query_one(StateCard).update_state(None, 0)
        self.step_forward()
        self.update_status()

    def step_forward(self):
        if self.mode == "INSERT":
            return
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            step = self.history[self.history_idx]
            self.steps = self.history_idx + 1
            self.apply_step(step)
            return

        if self.gen is None:
            return

        try:
            step = next(self.gen)
            self.history.append(step)
            self.history_idx = len(self.history) - 1
            self.steps = self.history_idx + 1
            self.apply_step(step)
        except StopIteration:
            self.gen = None
            self.stop_playing()
            self.update_status()

    def step_backward(self):
        if self.mode == "INSERT":
            return
        if self.history_idx > 0:
            self.history_idx -= 1
            self.steps = self.history_idx + 1
            step = self.history[self.history_idx]
            self.apply_step(step)
            if self.playing:
                self.stop_playing()

    def apply_step(self, step):
        self.query_one(Canvas).show(step)
        self.query_one(StateCard).update_state(step, self.steps)
        trace_data = [(i + 1, s.message) for i, s in enumerate(self.history[: self.history_idx + 1])]
        self.query_one(TraceView).set_history(trace_data, self.history_idx)
        self.update_status()

    def delay(self):
        return 0.02 + (100 - self.speed) * 0.008

    def set_playing(self, playing: bool):
        self.playing = playing
        self.mode = "RUNNING" if playing else "NORMAL"
        self.query_one(VimKeymap).update_state(self.speed, playing)
        self.update_status()

        if self.timer:
            self.timer.stop()
            self.timer = None
        if playing:
            self.timer = self.set_interval(self.delay(), self.step_forward)

    def stop_playing(self):
        self.set_playing(False)

    def update_status(self):
        mode = "INSERT" if self.mode == "INSERT" else ("RUNNING" if self.playing else "NORMAL")
        self.query_one(VimStatusBar).update_status(mode, self.current_cat, self.current_algo, self.steps)

    def action_toggle(self):
        if self.mode == "INSERT":
            return
        if self.gen is None and self.history_idx >= len(self.history) - 1:
            self.load()
        self.set_playing(not self.playing)

    def action_handle_left(self):
        if self.mode == "INSERT":
            return
        if self.playing or self.history_idx > 0:
            self.step_backward()
        else:
            self.action_prev_cat()

    def action_handle_right(self):
        if self.mode == "INSERT":
            return
        if self.playing or self.history_idx > 0:
            self.step_forward()
        else:
            self.action_next_cat()

    def action_step_forward(self):
        if self.mode == "INSERT":
            return
        self.stop_playing()
        self.step_forward()

    def action_step_backward(self):
        if self.mode == "INSERT":
            return
        self.stop_playing()
        self.step_backward()

    def action_reset(self):
        if self.mode == "INSERT":
            return
        self.load()

    def action_next_algo(self):
        if self.mode == "INSERT":
            return
        self.query_one(AlgoList).select_next()

    def action_prev_algo(self):
        if self.mode == "INSERT":
            return
        self.query_one(AlgoList).select_prev()

    def action_next_cat(self):
        if self.mode == "INSERT":
            return
        self.query_one(CategoryBar).next_cat()

    def action_prev_cat(self):
        if self.mode == "INSERT":
            return
        self.query_one(CategoryBar).prev_cat()

    def action_cat_1(self):
        if self.mode != "INSERT":
            self.set_category("Сортировки")

    def action_cat_2(self):
        if self.mode != "INSERT":
            self.set_category("Массивы")

    def action_cat_3(self):
        if self.mode != "INSERT":
            self.set_category("Поиск")

    def action_cat_4(self):
        if self.mode != "INSERT":
            self.set_category("Жадные")

    def action_slower(self):
        if self.mode == "INSERT":
            return
        self.speed = max(0, self.speed - 10)
        self.query_one(VimKeymap).update_state(self.speed, self.playing)
        if self.playing:
            self.set_playing(True)

    def action_faster(self):
        if self.mode == "INSERT":
            return
        self.speed = min(100, self.speed + 10)
        self.query_one(VimKeymap).update_state(self.speed, self.playing)
        if self.playing:
            self.set_playing(True)

    def action_edit(self):
        if self.mode == "INSERT":
            return
        self.stop_playing()
        self.mode = "INSERT"
        inp = self.query_one("#input_p1", Input)
        inp.focus()
        self.update_status()

    def action_cancel_edit(self):
        if self.mode != "INSERT":
            return
        self.mode = "NORMAL"
        self.update_numbers_ui()
        self.set_focus(None)
        self.update_status()

    def apply_inputs(self):
        self.current_p1 = self.query_one("#input_p1", Input).value
        if self.current_cat in ("Массивы", "Поиск", "Жадные"):
            self.current_p2 = self.query_one("#input_p2", Input).value
        self.mode = "NORMAL"
        self.set_focus(None)
        self.load()

    def on_input_submitted(self, _):
        self.apply_inputs()

    def on_button_pressed(self, event):
        if event.button.id == "btn_rand":
            self.action_rand()
        elif event.button.id == "btn_apply":
            self.apply_inputs()

    def on_input_changed(self, _):
        if self.focused and isinstance(self.focused, Input) and self.mode != "INSERT":
            self.mode = "INSERT"
            self.update_status()

    def action_rand(self):
        if self.current_cat == "Сортировки":
            count = random.randint(7, 12)
            vals = [random.randint(1, 30) for _ in range(count)]
            self.p1_sort = ", ".join(map(str, vals))
        elif self.current_cat == "Массивы":
            if self.current_algo == "Два указателя":
                count = random.randint(7, 10)
                vals = sorted(random.sample(range(1, 40), count))
                if random.random() < 0.75:
                    i, j = random.sample(range(count), 2)
                    target = vals[i] + vals[j]
                else:
                    target = random.randint(10, 70)
                self.p1_arrays = ", ".join(map(str, vals))
                self.p2_arrays = str(target)
            else:
                count = random.randint(6, 9)
                vals = [random.randint(1, 9) for _ in range(count)]
                ql = random.randint(0, count - 3)
                qr = random.randint(ql + 1, count - 1)
                self.p1_arrays = ", ".join(map(str, vals))
                self.p2_arrays = f"{ql} {qr}"
        elif self.current_cat == "Поиск":
            count = random.randint(8, 12)
            vals = sorted(random.sample(range(1, 60), count))
            target = random.choice(vals) if random.random() < 0.75 else random.randint(1, 60)
            self.p1_search = ", ".join(map(str, vals))
            self.p2_search = str(target)
        else:
            amount = random.randint(25, 240)
            self.p1_greedy = str(amount)

        self.update_numbers_ui()
        self.load()

    def on_category_bar_selected(self, event):
        self.set_category(event.cat)

    def on_algo_list_selected(self, event):
        self.set_algorithm(event.name)

    def on_vim_keymap_action(self, event):
        act = event.act
        if act == "toggle":
            self.action_toggle()
        elif act == "step_forward":
            self.action_step_forward()
        elif act == "step_backward":
            self.action_step_backward()
        elif act == "reset":
            self.action_reset()
        elif act == "next_algo":
            self.action_next_algo()
        elif act == "next_cat":
            self.action_next_cat()
        elif act == "speed_up":
            self.action_faster()
        elif act == "edit":
            self.action_edit()
        elif act == "rand":
            self.action_rand()
        elif act == "quit":
            self.exit()


def main():
    Algoss().run()


if __name__ == "__main__":
    main()
