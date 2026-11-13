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


IF_CODE = [
    "for i in range(len(data)):",
    "    x = data[i]",
    "    if x % 2 == 0:",
    "        evens += 1",
    "    else:",
    "        odds += 1",
]

WHILE_CODE = [
    "n = 7",
    "steps = 0",
    "while n != 1:",
    "    if n % 2 == 0:",
    "        n = n // 2",
    "    else:",
    "        n = 3 * n + 1",
    "    steps += 1",
]

IF_DATA = [4, 7, 2, 9, 6, 3, 8]


def for_if(data=IF_DATA):
    evens = 0
    odds = 0
    yield Step(list(data), (), (), 0, "Заходим в цикл", {"i": "—", "evens": 0, "odds": 0})
    for i in range(len(data)):
        x = data[i]
        yield Step(
            list(data),
            (i,),
            (),
            1,
            f"x = data[{i}] = {x}",
            {"i": i, "x": x, "evens": evens, "odds": odds},
        )
        if x % 2 == 0:
            yield Step(
                list(data),
                (i,),
                (),
                2,
                f"{x} чётное, условие истинно",
                {"i": i, "x": x, "evens": evens, "odds": odds},
            )
            evens += 1
            yield Step(
                list(data),
                (i,),
                (),
                3,
                f"evens = {evens}",
                {"i": i, "x": x, "evens": evens, "odds": odds},
            )
        else:
            yield Step(
                list(data),
                (i,),
                (),
                4,
                f"{x} нечётное, идём в else",
                {"i": i, "x": x, "evens": evens, "odds": odds},
            )
            odds += 1
            yield Step(
                list(data),
                (i,),
                (),
                5,
                f"odds = {odds}",
                {"i": i, "x": x, "evens": evens, "odds": odds},
            )
    yield Step(
        list(data),
        (),
        tuple(range(len(data))),
        0,
        f"Чётных {evens}, нечётных {odds}",
        {"evens": evens, "odds": odds},
    )


def collatz(start=7):
    n = start
    steps = 0
    seen = [n]
    yield Step(seen[:], (0,), (), 0, f"n = {n}", {"n": n, "steps": steps})
    while n != 1:
        yield Step(
            seen[:],
            (len(seen) - 1,),
            (),
            2,
            f"n = {n}, условие цикла истинно",
            {"n": n, "steps": steps},
        )
        if n % 2 == 0:
            yield Step(
                seen[:],
                (len(seen) - 1,),
                (),
                3,
                f"{n} чётное",
                {"n": n, "steps": steps},
            )
            n = n // 2
            line = 4
        else:
            yield Step(
                seen[:],
                (len(seen) - 1,),
                (),
                6,
                f"{n} нечётное",
                {"n": n, "steps": steps},
            )
            n = 3 * n + 1
            line = 6
        steps += 1
        seen.append(n)
        yield Step(
            seen[:],
            (len(seen) - 1,),
            (),
            line,
            f"n = {n}, steps = {steps}",
            {"n": n, "steps": steps},
        )
    yield Step(
        seen[:],
        (),
        tuple(range(len(seen) - 1)),
        2,
        f"Дошли до 1 за {steps} шагов",
        {"n": 1, "steps": steps},
    )


def coins(amount=137, nominal=(50, 25, 10, 5, 2, 1)):
    chosen = []
    rest = amount
    for coin in nominal:
        yield Step(
            chosen[:],
            (),
            (),
            message=f"Проверяем {coin}, остаток {rest}",
            vars={
                "монета": coin,
                "остаток": rest,
                "сумма": amount - rest,
                "монет": len(chosen),
            },
        )
        while rest >= coin:
            rest -= coin
            chosen.append(coin)
            yield Step(
                chosen[:],
                (len(chosen) - 1,),
                (),
                message=f"Берём {coin}, остаток {rest}",
                vars={
                    "монета": coin,
                    "остаток": rest,
                    "сумма": amount - rest,
                    "монет": len(chosen),
                },
            )
    yield Step(
        chosen[:],
        (),
        tuple(range(len(chosen))),
        message=f"Готово: {sum(chosen)} из {amount}",
        vars={"монет": len(chosen), "сумма": sum(chosen)},
    )


PROGRAMS = {
    "Сортировки": {
        "Пузырьковая": Program(lambda: bubble(DATA)),
        "Выбором": Program(lambda: selection(DATA)),
    },
    "Основы": {
        "Цикл for и if/else": Program(lambda: for_if(), IF_CODE),
        "Цикл while": Program(lambda: collatz(), WHILE_CODE),
    },
    "Жадные": {
        "Размен монетами": Program(lambda: coins()),
    },
}
