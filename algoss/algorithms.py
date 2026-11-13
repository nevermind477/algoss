from dataclasses import dataclass, field
from typing import Callable, Iterator

from .steps import Step

DATA = [7, 3, 9, 1, 5, 8, 2, 6]


def bubble(values):
    a = list(values)
    n = len(a)
    done: tuple[int, ...] = ()
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            yield Step(
                a[:],
                (j, j + 1),
                done,
                message=f"Сравнение A[{j}]={a[j]} и A[{j + 1}]={a[j + 1]}",
                vars={"i": i, "j": j, "swapped": swapped},
            )
            if a[j] > a[j + 1]:
                left, right = a[j], a[j + 1]
                a[j], a[j + 1] = right, left
                swapped = True
                yield Step(
                    a[:],
                    (j, j + 1),
                    done,
                    message=f"Обмен: {left} ⇄ {right}",
                    vars={"i": i, "j": j, "swapped": swapped},
                )
        done = tuple(range(n - i - 1, n))
        yield Step(
            a[:],
            (),
            done,
            message=f"{a[n - i - 1]} встал на место",
            vars={"i": i, "swapped": swapped},
        )
        if not swapped:
            break
    yield Step(a[:], (), tuple(range(n)), message="Массив отсортирован", vars={})


def selection(values):
    a = list(values)
    n = len(a)
    done: tuple[int, ...] = ()
    for i in range(n - 1):
        m = i
        yield Step(
            a[:],
            (i,),
            done,
            message=f"Ищем минимум с позиции {i}",
            vars={"i": i, "min": m},
        )
        for j in range(i + 1, n):
            yield Step(
                a[:],
                (m, j),
                done,
                message=f"Сравнение A[{m}]={a[m]} и A[{j}]={a[j]}",
                vars={"i": i, "min": m, "j": j},
            )
            if a[j] < a[m]:
                m = j
                yield Step(
                    a[:],
                    (m,),
                    done,
                    message=f"Новый минимум: {a[m]}",
                    vars={"i": i, "min": m, "j": j},
                )
        if m != i:
            a[i], a[m] = a[m], a[i]
            yield Step(
                a[:],
                (i, m),
                done,
                message=f"Ставим {a[i]} на позицию {i}",
                vars={"i": i, "min": m},
            )
        done += (i,)
        yield Step(
            a[:],
            (),
            done,
            message=f"Позиция {i} закрыта: {a[i]}",
            vars={"i": i},
        )
    yield Step(a[:], (), tuple(range(n)), message="Массив отсортирован", vars={})


@dataclass
class Program:
    run: Callable[[], Iterator[Step]]
    code: list[str] = field(default_factory=list)


PROGRAMS = {
    "Сортировки": {
        "Пузырьковая": Program(lambda: bubble(DATA)),
        "Выбором": Program(lambda: selection(DATA)),
    },
}
