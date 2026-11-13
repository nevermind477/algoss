from rich.text import Text
from textual.message import Message
from textual.widget import Widget

YELLOW = "#ffd700"
WHITE = "#ffffff"
GRAY = "#888888"
DARK_GRAY = "#444444"


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
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=GRAY)

        if not self.step or not self.step.array:
            out.append(f"│{'ожидание данных':^{width - 2}}│\n", style=DARK_GRAY)
            out.append(f"└{'─' * (width - 2)}┘", style=GRAY)
            return out

        values = self.step.array
        n = len(values)
        inner_w = width - 2
        slot = max(3, min(7, inner_w // n))
        total_w = slot * n
        pad_left = max(0, (inner_w - total_w) // 2)
        pad_right = max(0, inner_w - total_w - pad_left)

        top = max(values) if values and max(values) > 0 else 1
        canvas_h = max(5, self.size.height - 6)

        for row in range(canvas_h, 0, -1):
            out.append("│", style=GRAY)
            out.append(" " * pad_left)
            for i, val in enumerate(values):
                filled = max(1, round(val / top * canvas_h))
                if filled >= row:
                    if i in self.step.active:
                        style = f"bold {YELLOW}"
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
            out.append("│\n", style=GRAY)

        out.append("│", style=GRAY)
        out.append(" " * pad_left)
        for i in range(n):
            ptr_labels = [k for k, v in self.step.pointers.items() if v == i]
            if ptr_labels:
                lbl = "/".join(ptr_labels)
                out.append(f"{lbl:^{slot}}"[:slot], style=f"bold {YELLOW}")
            elif i in self.step.active:
                out.append(f"{'▲':^{slot}}", style=f"bold {YELLOW}")
            elif i in self.step.done:
                out.append(f"{'•':^{slot}}", style=DARK_GRAY)
            else:
                out.append(" " * slot)
        out.append(" " * pad_right)
        out.append("│\n", style=GRAY)

        out.append("│", style=GRAY)
        out.append(" " * pad_left)
        for i, val in enumerate(values):
            if i in self.step.active:
                style = f"bold {YELLOW}"
            elif i in self.step.done:
                style = f"bold {WHITE}"
            else:
                style = GRAY
            out.append(f"{val:^{slot}}", style=style)
        out.append(" " * pad_right)
        out.append("│\n", style=GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=GRAY)
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
            if len(self.history) > 50:
                self.history.pop(0)
            self.refresh()

    def render(self):
        width = max(self.size.width, 20)
        height = max(self.size.height, 4)
        out = Text()

        title = " ЖУРНАЛ ШАГОВ "
        fill_len = max(0, width - len(title) - 4)
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=GRAY)

        visible_rows = height - 2
        items = self.history[-visible_rows:] if self.history else []
        pad_empty = visible_rows - len(items)

        for _ in range(pad_empty):
            out.append(f"│{' ' * (width - 2)}│\n", style=GRAY)

        for idx, (s_num, msg) in enumerate(items):
            is_last = (idx == len(items) - 1)
            marker = "▶" if is_last else " "
            prefix = f" {marker} #{s_num:<3} │ "
            content_w = width - 2 - len(prefix)
            line = msg[:content_w] if len(msg) > content_w else msg
            tail = " " * max(0, content_w - len(line))

            out.append("│", style=GRAY)
            out.append(prefix, style=f"bold {YELLOW}" if is_last else GRAY)
            out.append(line, style=f"bold {YELLOW}" if is_last else WHITE)
            out.append(tail)
            out.append("│\n", style=GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=GRAY)
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
        out.append(f"┌─{title}{'─' * fill_len}┐\n", style=GRAY)

        inner_w = width - 2
        if not self.step:
            msg = " Ожидание запуска алгоритма..."
            out.append(f"│{msg:<{inner_w}}│\n", style=DARK_GRAY)
            out.append(f"│{' ' * inner_w}│\n", style=DARK_GRAY)
            out.append(f"└{'─' * (width - 2)}┘", style=GRAY)
            return out

        msg = f" Шаг {self.step_num}: {self.step.message}"
        truncated_msg = msg[:inner_w]
        tail_msg = " " * (inner_w - len(truncated_msg))
        out.append("│", style=GRAY)
        out.append(truncated_msg, style=f"bold {YELLOW}")
        out.append(tail_msg)
        out.append("│\n", style=GRAY)

        badges = []
        for k, v in self.step.vars.items():
            badges.append(f"[{k}: {v}]")
        var_line = "  " + "  ".join(badges) if badges else "  (нет локальных переменных)"
        truncated_vars = var_line[:inner_w]
        tail_vars = " " * (inner_w - len(truncated_vars))
        out.append("│", style=GRAY)
        out.append(truncated_vars, style=f"bold {WHITE}")
        out.append(tail_vars)
        out.append("│\n", style=GRAY)

        out.append(f"└{'─' * (width - 2)}┘", style=GRAY)
        return out


class SpeedBar(Widget):
    can_focus = True
    BINDINGS = [
        ("left", "slower", "медленнее"),
        ("right", "faster", "быстрее"),
    ]

    class Changed(Message):
        def __init__(self, value: int):
            super().__init__()
            self.value = value

    def __init__(self, value=50, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def render(self):
        total_slots = 12
        filled = round(self.value / 100 * total_slots)
        out = Text()
        out.append("скорость [ ", style=GRAY)
        for i in range(total_slots):
            if i < filled:
                out.append("■", style=f"bold {YELLOW}" if i == filled - 1 else WHITE)
            else:
                out.append("─", style=DARK_GRAY)
        out.append(f" ] {self.value:>3}%", style=f"bold {YELLOW}")
        return out

    def on_click(self, event):
        event.stop()
        slot = min(max(event.offset.x - 11, 0), 12)
        self.set_value(round(slot / 12 * 100))

    def set_value(self, value):
        value = min(max(int(value), 0), 100)
        if value != self.value:
            self.value = value
            self.refresh()
            self.post_message(self.Changed(value))

    def action_slower(self):
        self.set_value(self.value - 5)

    def action_faster(self):
        self.set_value(self.value + 5)
