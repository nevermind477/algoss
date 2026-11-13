from rich.text import Text
from textual.message import Message
from textual.widget import Widget

WHITE = "#ffffff"
GRAY = "#888888"
DARK_GRAY = "#444444"
DIM = "#222222"


class LogoView(Widget):
    def render(self):
        width = max(self.size.width, 24)
        out = Text()

        if width >= 36:
            lines = [
                "  ___   _    ___  ___  ___ ___  ",
                " / _ \\ | |  / _ \\/ _ \\/ __/ __| ",
                "/ ___ \\| |__\\ (_) \\ (_) \\__ \\__ \\",
                "/_/   \\_\\_____\\___/ \\___/|___/___/",
            ]
        else:
            lines = [
                "█▀█ █ █▀▀ █▀█ █▀▀ █▀▀",
                "█▀█ █ █ █ █ █ ▀▀█ ▀▀█",
                "▀ ▀ ▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀",
            ]

        inner = width - 2
        title = " ALGOSS "
        fill = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill}┐\n", style=DARK_GRAY)

        for l in lines:
            if len(l) > inner:
                row = l[:inner]
            else:
                pad = (inner - len(l)) // 2
                row = (" " * pad) + l + (" " * (inner - len(l) - pad))
            out.append("│", style=DARK_GRAY)
            out.append(row, style=f"bold {WHITE}")
            out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * inner}┘", style=DARK_GRAY)
        return out


class CategoryBar(Widget):
    can_focus = False

    class Selected(Message):
        def __init__(self, cat: str):
            super().__init__()
            self.cat = cat

    def __init__(self, categories: list[str], current: str, **kwargs):
        super().__init__(**kwargs)
        self.categories = categories
        self.current = current

    def set_current(self, cat: str):
        if cat in self.categories and cat != self.current:
            self.current = cat
            self.refresh()
            self.post_message(self.Selected(cat))

    def next_cat(self):
        idx = (self.categories.index(self.current) + 1) % len(self.categories)
        self.set_current(self.categories[idx])

    def prev_cat(self):
        idx = (self.categories.index(self.current) - 1) % len(self.categories)
        self.set_current(self.categories[idx])

    def render(self):
        width = max(self.size.width, 24)
        out = Text()
        title = " РЕЖИМ [h/l или 1-3] "
        fill = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill}┐\n", style=DARK_GRAY)

        out.append("│ ", style=DARK_GRAY)
        used_len = 2
        for idx, cat in enumerate(self.categories, start=1):
            is_active = (cat == self.current)
            short_name = "Сорт" if cat == "Сортировки" else cat
            label = f"{idx}: {short_name}"
            if is_active:
                out.append(f"[{label}]", style=f"bold #000000 on {WHITE}")
                used_len += len(label) + 2
            else:
                out.append(f" {label} ", style=GRAY)
                used_len += len(label) + 2
            out.append(" ")
            used_len += 1

        rem = max(0, width - 1 - used_len)
        out.append(" " * rem)
        out.append("│\n", style=DARK_GRAY)
        out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
        return out

    def on_click(self, event):
        x = event.offset.x
        if x < 15:
            self.set_current(self.categories[0])
        elif x < 26 and len(self.categories) > 1:
            self.set_current(self.categories[1])
        elif len(self.categories) > 2:
            self.set_current(self.categories[2])


class AlgoList(Widget):
    can_focus = False

    class Selected(Message):
        def __init__(self, name: str):
            super().__init__()
            self.name = name

    def __init__(self, items: list[str], current: str, **kwargs):
        super().__init__(**kwargs)
        self.items = items
        self.current = current

    def set_items(self, items: list[str], current: str):
        self.items = items
        self.current = current if current in items else items[0]
        self.refresh()

    def select_next(self):
        if not self.items:
            return
        idx = (self.items.index(self.current) + 1) % len(self.items)
        self.current = self.items[idx]
        self.refresh()
        self.post_message(self.Selected(self.current))

    def select_prev(self):
        if not self.items:
            return
        idx = (self.items.index(self.current) - 1) % len(self.items)
        self.current = self.items[idx]
        self.refresh()
        self.post_message(self.Selected(self.current))

    def select_index(self, idx: int):
        if 0 <= idx < len(self.items):
            self.current = self.items[idx]
            self.refresh()
            self.post_message(self.Selected(self.current))

    def render(self):
        width = max(self.size.width, 24)
        out = Text()
        title = " АЛГОРИТМ [j/k] "
        fill = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill}┐\n", style=DARK_GRAY)

        inner = width - 2
        for i, item in enumerate(self.items, start=1):
            is_active = (item == self.current)
            cursor = "▸" if is_active else " "
            row_text = f" {cursor} {i}. {item}"
            padded = f"{row_text:<{inner}}"[:inner]

            out.append("│", style=DARK_GRAY)
            if is_active:
                out.append(padded, style=f"bold {WHITE} on {DARK_GRAY}")
            else:
                out.append(padded, style=GRAY)
            out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * inner}┘", style=DARK_GRAY)
        return out

    def on_click(self, event):
        idx = event.offset.y - 1
        if 0 <= idx < len(self.items):
            self.select_index(idx)


class ParamsView(Widget):
    can_focus = False

    class EditRequested(Message):
        pass

    class RandRequested(Message):
        pass

    def __init__(self, cat: str, p1: str, p2: str = "", **kwargs):
        super().__init__(**kwargs)
        self.cat = cat
        self.p1 = p1
        self.p2 = p2

    def update_params(self, cat: str, p1: str, p2: str = ""):
        self.cat = cat
        self.p1 = p1
        self.p2 = p2
        self.refresh()

    def render(self):
        width = max(self.size.width, 24)
        inner = width - 2
        out = Text()
        title = " ПАРАМЕТРЫ [i: правка, g: rand] "
        fill = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill}┐\n", style=DARK_GRAY)

        if self.cat == "Сортировки":
            line = f" Массив: [{self.p1}]"
        elif self.cat == "Поиск":
            line = f" Массив: [{self.p1}] | Цель: {self.p2}"
        else:
            line = f" Сумма: {self.p1} | Монеты: [{self.p2}]"

        padded = f"{line:<{inner}}"[:inner]
        out.append("│", style=DARK_GRAY)
        out.append(padded, style=f"bold {WHITE}")
        out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * inner}┘", style=DARK_GRAY)
        return out

    def on_click(self, event):
        self.post_message(self.EditRequested())


class VimKeymap(Widget):
    can_focus = False

    class Action(Message):
        def __init__(self, act: str):
            super().__init__()
            self.act = act

    def __init__(self, speed: int = 50, playing: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.playing = playing

    def update_state(self, speed: int, playing: bool):
        self.speed = speed
        self.playing = playing
        self.refresh()

    def render(self):
        width = max(self.size.width, 24)
        inner = width - 2
        out = Text()
        title = " УПРАВЛЕНИЕ [VIM] "
        fill = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill}┐\n", style=DARK_GRAY)

        play_label = "пауза" if self.playing else "старт"
        lines = [
            f"<space>  {play_label:<12} n    шаг",
            "j / k    алгоритм      r    сброс",
            "h / l    режим (1-3)   q    выход",
            f"i / g    правка/rand  -/+   скорость: {self.speed}%",
        ]

        for l in lines:
            padded = f" {l:<{inner - 1}}"[:inner]
            out.append("│", style=DARK_GRAY)
            out.append(padded, style=GRAY)
            out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * inner}┘", style=DARK_GRAY)
        return out

    def on_click(self, event):
        y = event.offset.y
        if y == 1:
            if event.offset.x < 18:
                self.post_message(self.Action("toggle"))
            else:
                self.post_message(self.Action("step"))
        elif y == 2:
            if event.offset.x < 18:
                self.post_message(self.Action("next_algo"))
            else:
                self.post_message(self.Action("next_cat"))
        elif y == 3:
            if event.offset.x < 18:
                self.post_message(self.Action("reset"))
            else:
                self.post_message(self.Action("speed_up"))
        elif y == 4:
            if event.offset.x < 18:
                self.post_message(self.Action("edit"))
            else:
                self.post_message(self.Action("rand"))


class VimStatusBar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "NORMAL"
        self.algo = "Пузырьковая"
        self.cat = "Сортировки"
        self.step_num = 0

    def update_status(self, mode: str, cat: str, algo: str, step_num: int):
        self.mode = mode
        self.cat = cat
        self.algo = algo
        self.step_num = step_num
        self.refresh()

    def render(self):
        width = max(self.size.width, 30)
        out = Text()

        if self.mode == "INSERT":
            out.append(" INSERT ", style=f"bold #000000 on {WHITE}")
            out.append(" [Enter] применить   [Esc] отмена   ", style=f"bold {WHITE} on {DARK_GRAY}")
        elif self.mode == "RUNNING":
            out.append(" RUNNING ", style=f"bold #000000 on {WHITE}")
            out.append(f" {self.cat} ▸ {self.algo} │ шаг {self.step_num}   ", style=f"bold {WHITE} on {DARK_GRAY}")
        else:
            out.append(" NORMAL ", style=f"bold #000000 on {WHITE}")
            out.append(f" {self.cat} ▸ {self.algo} │ шаг {self.step_num}   ", style=f"{WHITE} on {DARK_GRAY}")

        hint = " <space> старт  n шаг  r сброс  i правка  g rand  q выход "
        used = len(out.plain)
        rem = max(0, width - used - len(hint))
        out.append(" " * rem, style=f"on {DARK_GRAY}")
        out.append(hint, style=f"bold {WHITE} on {DARK_GRAY}")
        return out


class Canvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = None

    def show(self, step):
        self.step = step
        self.refresh()

    def render(self):
        width = max(self.size.width, 20)
        out = Text()

        title = " ВИЗУАЛИЗАЦИЯ "
        fill_len = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=DARK_GRAY)

        if not self.step or not self.step.array:
            out.append(f"│{'ожидание данных':^{width - 2}}│\n", style=DARK_GRAY)
            out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
            return out

        values = self.step.array
        n = len(values)
        inner_w = width - 2
        slot = max(3, min(7, inner_w // n))
        total_w = slot * n
        pad_left = max(0, (inner_w - total_w) // 2)
        pad_right = max(0, inner_w - total_w - pad_left)

        top = max(values) if values and max(values) > 0 else 1
        canvas_h = max(5, self.size.height - 5)

        for row in range(canvas_h, 0, -1):
            out.append("│", style=DARK_GRAY)
            out.append(" " * pad_left)
            for i, val in enumerate(values):
                filled = max(1, round(val / top * canvas_h))
                if filled >= row:
                    if i in self.step.active:
                        style = f"bold {WHITE}"
                        char = "██"
                    elif i in self.step.done:
                        style = f"bold {WHITE}"
                        char = "██"
                    else:
                        style = DARK_GRAY
                        char = "▓▓"
                    out.append(f"{char:^{slot}}", style=style)
                else:
                    out.append(" " * slot)
            out.append(" " * pad_right)
            out.append("│\n", style=DARK_GRAY)

        out.append("│", style=DARK_GRAY)
        out.append(" " * pad_left)
        for i in range(n):
            ptr_labels = [k for k, v in self.step.pointers.items() if v == i]
            if ptr_labels:
                lbl = "/".join(ptr_labels)
                out.append(f"{lbl:^{slot}}"[:slot], style=f"bold {WHITE}")
            elif i in self.step.active:
                out.append(f"{'▲':^{slot}}", style=f"bold {WHITE}")
            elif i in self.step.done:
                out.append(f"{'•':^{slot}}", style=GRAY)
            else:
                out.append(" " * slot)
        out.append(" " * pad_right)
        out.append("│\n", style=DARK_GRAY)

        out.append("│", style=DARK_GRAY)
        out.append(" " * pad_left)
        for i in range(n):
            val = values[i]
            if i in self.step.active:
                style = f"bold {WHITE}"
            elif i in self.step.done:
                style = f"bold {WHITE}"
            else:
                style = GRAY
            out.append(f"{val:^{slot}}", style=style)
        out.append(" " * pad_right)
        out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
        return out


class TraceView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history: list[tuple[int, str]] = []

    def clear(self):
        self.history.clear()
        self.refresh()

    def add(self, step_num: int, message: str):
        if not self.history or self.history[-1] != (step_num, message):
            self.history.append((step_num, message))
            if len(self.history) > 60:
                self.history.pop(0)
            self.refresh()

    def render(self):
        width = max(self.size.width, 20)
        height = max(self.size.height, 4)
        out = Text()

        title = " ЖУРНАЛ ШАГОВ "
        fill_len = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=DARK_GRAY)

        visible_rows = height - 2
        items = self.history[-visible_rows:] if self.history else []
        pad_empty = visible_rows - len(items)

        for _ in range(pad_empty):
            out.append(f"│{' ' * (width - 2)}│\n", style=DARK_GRAY)

        for idx, (s_num, msg) in enumerate(items):
            is_last = (idx == len(items) - 1)
            marker = "▶" if is_last else " "
            prefix = f" {marker} #{s_num:<3} │ "
            content_w = width - 2 - len(prefix)
            line = msg[:content_w] if len(msg) > content_w else msg
            tail = " " * max(0, content_w - len(line))

            out.append("│", style=DARK_GRAY)
            out.append(prefix, style=f"bold {WHITE}" if is_last else DARK_GRAY)
            out.append(line, style=f"bold {WHITE}" if is_last else GRAY)
            out.append(tail)
            out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
        return out


class StateCard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = None
        self.step_num = 0

    def update_state(self, step, step_num: int):
        self.step = step
        self.step_num = step_num
        self.refresh()

    def render(self):
        width = max(self.size.width, 20)
        out = Text()

        title = " ТЕКУЩЕЕ ДЕЙСТВИЕ И ПЕРЕМЕННЫЕ "
        fill_len = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=DARK_GRAY)

        inner_w = width - 2
        if not self.step:
            msg = " Ожидание запуска алгоритма..."
            out.append(f"│{msg:<{inner_w}}│\n", style=DARK_GRAY)
            out.append(f"│{' ' * inner_w}│\n", style=DARK_GRAY)
            out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
            return out

        msg = f" Шаг {self.step_num}: {self.step.message}"
        truncated_msg = msg[:inner_w]
        tail_msg = " " * (inner_w - len(truncated_msg))
        out.append("│", style=DARK_GRAY)
        out.append(truncated_msg, style=f"bold {WHITE}")
        out.append(tail_msg)
        out.append("│\n", style=DARK_GRAY)

        badges = []
        for k, v in self.step.vars.items():
            badges.append(f"[{k}: {v}]")
        var_line = "  " + "  ".join(badges) if badges else "  (нет локальных переменных)"
        truncated_vars = var_line[:inner_w]
        tail_vars = " " * (inner_w - len(truncated_vars))
        out.append("│", style=DARK_GRAY)
        out.append(truncated_vars, style=GRAY)
        out.append(tail_vars)
        out.append("│\n", style=DARK_GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=DARK_GRAY)
        return out
