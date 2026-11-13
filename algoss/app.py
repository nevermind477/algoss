import random
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input

from .algorithms import (
    DEFAULT_COINS,
    DEFAULT_SEARCH,
    DEFAULT_SORT,
    binary_search,
    bubble,
    coin_change,
    insertion,
    linear_search,
    mergesort,
    quicksort,
    selection,
    shaker,
)
from .views import (
    AlgoList,
    Canvas,
    CategoryBar,
    LogoView,
    ParamsView,
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
        ("n", "step", "шаг"),
        ("right", "step", "шаг"),
        ("r", "reset", "сброс"),
        ("j", "next_algo", "след. алгоритм"),
        ("down", "next_algo", "след. алгоритм"),
        ("k", "prev_algo", "пред. алгоритм"),
        ("up", "prev_algo", "пред. алгоритм"),
        ("h", "prev_cat", "пред. режим"),
        ("left", "prev_cat", "пред. режим"),
        ("l", "next_cat", "след. режим"),
        ("1", "cat_1", "режим 1"),
        ("2", "cat_2", "режим 2"),
        ("3", "cat_3", "режим 3"),
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

        self.current_cat = "Сортировки"
        self.current_algo = "Пузырьковая"

        self.p1_sort = ", ".join(map(str, DEFAULT_SORT))
        self.p1_search = ", ".join(map(str, DEFAULT_SEARCH))
        self.p2_search = "23"
        self.p1_greedy = "137"
        self.p2_greedy = ", ".join(map(str, DEFAULT_COINS))

    @property
    def current_p1(self) -> str:
        if self.current_cat == "Сортировки":
            return self.p1_sort
        elif self.current_cat == "Поиск":
            return self.p1_search
        return self.p1_greedy

    @current_p1.setter
    def current_p1(self, val: str):
        if self.current_cat == "Сортировки":
            self.p1_sort = val
        elif self.current_cat == "Поиск":
            self.p1_search = val
        else:
            self.p1_greedy = val

    @property
    def current_p2(self) -> str:
        if self.current_cat == "Поиск":
            return self.p2_search
        return self.p2_greedy

    @current_p2.setter
    def current_p2(self, val: str):
        if self.current_cat == "Поиск":
            self.p2_search = val
        else:
            self.p2_greedy = val

    def compose(self) -> ComposeResult:
        with Horizontal(id="body"):
            with Vertical(id="side"):
                yield LogoView(id="logo")
                yield CategoryBar(list(CATEGORIES.keys()), self.current_cat, id="cat_bar")
                yield AlgoList(CATEGORIES[self.current_cat], self.current_algo, id="algo_list")
                yield ParamsView(self.current_cat, self.current_p1, self.current_p2, id="params_view")
                yield Input(self.current_p1, id="input_p1", classes="hidden")
                yield Input(self.current_p2, id="input_p2", classes="hidden")
                yield VimKeymap(self.speed, self.playing, id="keymap")

            with Vertical(id="main"):
                yield Canvas(id="canvas")
                yield StateCard(id="state")
                yield TraceView(id="trace")

        yield VimStatusBar(id="status_bar")

    def on_mount(self):
        self.query_one("#input_p1", Input).can_focus = False
        self.query_one("#input_p2", Input).can_focus = False
        self.set_focus(None)
        self.load()

    def set_category(self, cat: str):
        if cat not in CATEGORIES or cat == self.current_cat:
            return
        self.current_cat = cat
        self.query_one(CategoryBar).current = cat
        self.query_one(CategoryBar).refresh()

        algos = CATEGORIES[cat]
        self.current_algo = algos[0]
        self.query_one(AlgoList).set_items(algos, self.current_algo)
        self.update_params_display()
        self.load()

    def set_algorithm(self, name: str):
        if name in CATEGORIES[self.current_cat] and name != self.current_algo:
            self.current_algo = name
            self.query_one(AlgoList).current = name
            self.query_one(AlgoList).refresh()
            self.load()

    def update_params_display(self):
        self.query_one(ParamsView).update_params(self.current_cat, self.current_p1, self.current_p2)

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
        self.update_status()

    def advance(self):
        if self.gen is None:
            return
        try:
            step = next(self.gen)
        except StopIteration:
            self.gen = None
            self.stop_playing()
            self.update_status()
            return
        self.steps += 1
        self.query_one(Canvas).show(step)
        self.query_one(StateCard).update_state(step, self.steps)
        self.query_one(TraceView).add(self.steps, step.message)
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
            self.timer = self.set_interval(self.delay(), self.advance)

    def stop_playing(self):
        self.set_playing(False)

    def update_status(self):
        mode = "INSERT" if self.mode == "INSERT" else ("RUNNING" if self.playing else "NORMAL")
        self.query_one(VimStatusBar).update_status(mode, self.current_cat, self.current_algo, self.steps)

    def action_toggle(self):
        if self.mode == "INSERT":
            return
        if self.gen is None:
            self.load()
        self.set_playing(not self.playing)

    def action_step(self):
        if self.mode == "INSERT":
            return
        self.stop_playing()
        self.advance()

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
            self.set_category("Поиск")

    def action_cat_3(self):
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
        self.query_one(ParamsView).display = False

        inp1 = self.query_one("#input_p1", Input)
        inp1.can_focus = True
        inp1.value = self.current_p1
        inp1.display = True
        inp1.focus()

        if self.current_cat in ("Поиск", "Жадные"):
            inp2 = self.query_one("#input_p2", Input)
            inp2.can_focus = True
            inp2.value = self.current_p2
            inp2.display = True
        else:
            self.query_one("#input_p2", Input).display = False

        self.update_status()

    def action_cancel_edit(self):
        if self.mode != "INSERT":
            return
        self.mode = "NORMAL"
        inp1 = self.query_one("#input_p1", Input)
        inp2 = self.query_one("#input_p2", Input)
        inp1.can_focus = False
        inp2.can_focus = False
        inp1.display = False
        inp2.display = False
        self.query_one(ParamsView).display = True
        self.update_status()
        self.set_focus(None)

    def on_input_submitted(self, event):
        inp1 = self.query_one("#input_p1", Input)
        self.current_p1 = inp1.value
        if self.current_cat in ("Поиск", "Жадные"):
            inp2 = self.query_one("#input_p2", Input)
            self.current_p2 = inp2.value
        self.action_cancel_edit()
        self.update_params_display()
        self.load()

    def action_rand(self):
        if self.mode == "INSERT":
            return
        if self.current_cat == "Сортировки":
            count = random.randint(7, 12)
            vals = [random.randint(1, 30) for _ in range(count)]
            self.p1_sort = ", ".join(map(str, vals))
        elif self.current_cat == "Поиск":
            count = random.randint(8, 12)
            vals = sorted(random.sample(range(1, 60), count))
            target = random.choice(vals) if random.random() < 0.75 else random.randint(1, 60)
            self.p1_search = ", ".join(map(str, vals))
            self.p2_search = str(target)
        else:
            amount = random.randint(25, 240)
            self.p1_greedy = str(amount)

        self.update_params_display()
        self.load()

    def on_category_bar_selected(self, event):
        self.set_category(event.cat)

    def on_algo_list_selected(self, event):
        self.set_algorithm(event.name)

    def on_params_view_edit_requested(self, _):
        self.action_edit()

    def on_vim_keymap_action(self, event):
        act = event.act
        if act == "toggle":
            self.action_toggle()
        elif act == "step":
            self.action_step()
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


def main():
    Algoss().run()


if __name__ == "__main__":
    main()
