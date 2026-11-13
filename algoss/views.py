from rich.text import Text
from textual.message import Message
from textual.widget import Widget

ACCENT = "#f9e2af"
OK = "#a6e3a1"
BAR = "#7aa2f7"
DIM = "#565f6b"


class Canvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = None
        self.code: list[str] = []

    def show(self, step, code=None):
        self.step = step
        self.code = code or []
        self.refresh()

    def render(self):
        if self.step is None:
            return Text("ожидание", style=DIM)
        if self.code:
            return self.paint_code()
        return self.paint_bars()

    def paint_bars(self):
        values = self.step.array
        if not values:
            return Text("")
        top = max(values)
        height = max(self.size.height - 2, 1)
        out = Text()
        for row in range(height, 0, -1):
            for i, value in enumerate(values):
                filled = max(1, round(value / top * height))
                if filled >= row:
                    style = BAR
                    if i in self.step.active:
                        style = f"bold {ACCENT}"
                    elif i in self.step.done:
                        style = OK
                    out.append(" ██ ", style=style)
                else:
                    out.append("    ")
            out.append("\n")
        for i in range(len(values)):
            style = f"bold {ACCENT}" if i in self.step.active else DIM
            out.append(f"{i:^4}", style=style)
        return out

    def paint_code(self):
        out = Text()
        for i, value in enumerate(self.step.array):
            if i in self.step.active:
                style = f"bold {ACCENT}"
            elif i in self.step.done:
                style = OK
            else:
                style = DIM
            out.append(f"{value:^3}", style=style)
        out.append("\n\n")
        for n, line in enumerate(self.code):
            if n == self.step.line:
                out.append("▸ ", style=f"bold {ACCENT}")
                out.append(f"{line}\n", style=f"bold {ACCENT} on #1d2430")
            else:
                out.append(f"  {line}\n", style=DIM)
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
        filled = round(self.value / 100 * 10)
        out = Text()
        out.append("− ", style=DIM)
        for i in range(10):
            if i < filled:
                style = f"bold {ACCENT}" if i == filled - 1 else BAR
                out.append("▬", style=style)
            else:
                out.append("─", style=DIM)
        out.append(" +", style=DIM)
        return out

    def on_click(self, event):
        event.stop()
        slot = min(max(event.offset.x - 2, 0), 9)
        self.set_value(round(slot / 9 * 100))

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
