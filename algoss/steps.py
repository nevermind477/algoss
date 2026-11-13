from dataclasses import dataclass, field


@dataclass
class Step:
    array: list[int] = field(default_factory=list)
    active: tuple[int, ...] = ()
    done: tuple[int, ...] = ()
    line: int | None = None
    message: str = ""
    vars: dict[str, object] = field(default_factory=dict)
