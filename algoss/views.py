from rich.text import Text
from textual.message import Message
from textual.widget import Widget

WHITE = "#ffffff"
GRAY = "#888888"
DARK_GRAY = "#444444"
DIM = "#222222"


def box_top(title: str, width: int) -> str:
    prefix = f"┌─ {title} " if title else "┌─"
    fill = max(0, width - len(prefix) - 1)
    return prefix + ("─" * fill) + "┐\n"


def box_bot(width: int) -> str:
    return "└" + ("─" * max(0, width - 2)) + "┘"


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
        out.append(box_top("ALGOSS", width), style=DARK_GRAY)

        for l in lines:
            if len(l) > inner:
                row = l[:inner]
            else:
                pad = (inner - len(l)) // 2
                row = (" " * pad) + l + (" " * (inner - len(l) - pad))
            out.append("│", style=DARK_GRAY)
            out.append(row, style=f"bold {WHITE}")
            out.append("│\n", style=DARK_GRAY)

        out.append(box_bot(width), style=DARK_GRAY)
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
        out.append(box_top("РЕЖИМ [h/l или 1-3]", width), style=DARK_GRAY)

        inner = width - 2
        row = Text()
        row.append(" ")
        for idx, cat in enumerate(self.categories, start=1):
            is_active = (cat == self.current)
            sname = "Сорт" if cat == "Сортировки" else ("Жадн" if width < 36 and cat == "Жадные" else cat)
            if is_active:
                row.append(f"[{idx}:{sname}]", style=f"bold #000000 on {WHITE}")
            else:
                row.append(f" {idx}:{sname} ", style=GRAY)
            row.append(" ")

        if len(row.plain) > inner:
            row = row[:inner]
        else:
            row.append(" " * (inner - len(row.plain)))

        out.append("│", style=DARK_GRAY)
        out.append_text(row)
        out.append("│\n", style=DARK_GRAY)
        out.append(box_bot(width), style=DARK_GRAY)
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
        out.append(box_top("АЛГОРИТМ [j/k]", width), style=DARK_GRAY)

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

        out.append(box_bot(width), style=DARK_GRAY)
        return out

    def on_click(self, event):
        idx = event.offset.y - 1
        if 0 <= idx < len(self.items):
            self.select_index(idx)


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
        out.append(box_top("УПРАВЛЕНИЕ [VIM]", width), style=DARK_GRAY)

        play_label = "пауза" if self.playing else "старт"
        lines = [
            f"<space>  {play_label}",
            "n        шаг вперед",
            "r        сброс к началу",
            "j / k    выбор алгоритма",
            "h / l    смена режима (1-3)",
            "i        настройка чисел",
            "g        случайные числа",
            f"- / +    скорость: {self.speed}%",
            "q        выход",
        ]

        for l in lines:
            padded = f" {l:<{inner - 1}}"[:inner]
            out.append("│", style=DARK_GRAY)
            out.append(padded, style=GRAY)
            out.append("│\n", style=DARK_GRAY)

        out.append(box_bot(width), style=DARK_GRAY)
        return out

    def on_click(self, event):
        y = event.offset.y
        actions = [
            "toggle",
            "step",
            "reset",
            "next_algo",
            "next_cat",
            "edit",
            "rand",
            "speed_up",
            "quit",
        ]
        idx = y - 1
        if 0 <= idx < len(actions):
            self.post_message(self.Action(actions[idx]))


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

        hint = " <space> старт  n шаг  r сброс  i ввод  g rand  q выход "
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
        out.append(box_top("ВИЗУАЛИЗАЦИЯ", width), style=DARK_GRAY)

        if not self.step or not self.step.array:
            out.append(f"│{'ожидание данных':^{width - 2}}│\n", style=DARK_GRAY)
            out.append(box_bot(width), style=DARK_GRAY)
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

        out.append(box_bot(width), style=DARK_GRAY)
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
        out.append(box_top("ЖУРНАЛ ШАГОВ", width), style=DARK_GRAY)

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

        out.append(box_bot(width), style=DARK_GRAY)
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
        out.append(box_top("ТЕКУЩЕЕ ДЕЙСТВИЕ И ПЕРЕМЕННЫЕ", width), style=DARK_GRAY)

        inner_w = width - 2
        if not self.step:
            msg = " Ожидание запуска алгоритма..."
            out.append(f"│{msg:<{inner_w}}│\n", style=DARK_GRAY)
            out.append(f"│{' ' * inner_w}│\n", style=DARK_GRAY)
            out.append(box_bot(width), style=DARK_GRAY)
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

        out.append(box_bot(width), style=DARK_GRAY)
        return out
