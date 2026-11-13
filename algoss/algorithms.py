from typing import Iterator
from .steps import Step

DEFAULT_SORT = [14, 5, 22, 3, 11, 18, 8, 2, 9]
DEFAULT_TWO_POINTERS = [2, 4, 7, 11, 15, 19, 24, 30]
DEFAULT_PREFIX = [3, 2, 5, 1, 4, 3, 6, 2]
DEFAULT_SEARCH = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
DEFAULT_COINS = [50, 25, 10, 5, 2, 1]


def bubble(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    comps = 0
    swaps = 0
    done: tuple[int, ...] = ()
    yield Step(a[:], (), (), message="Начало пузырьковой сортировки", vars={"сравнений": 0, "обменов": 0})
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comps += 1
            yield Step(
                a[:],
                (j, j + 1),
                done,
                pointers={"j": j},
                message=f"Сравнение A[{j}]={a[j]} и A[{j + 1}]={a[j + 1]}",
                vars={"i": i, "j": j, "сравнений": comps, "обменов": swaps},
            )
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
                yield Step(
                    a[:],
                    (j, j + 1),
                    done,
                    pointers={"j": j},
                    message=f"Обмен: {a[j + 1]} ⇄ {a[j]}",
                    vars={"i": i, "j": j, "сравнений": comps, "обменов": swaps},
                )
        done = tuple(range(n - i - 1, n))
        yield Step(
            a[:],
            (),
            done,
            message=f"Элемент {a[n - i - 1]} зафиксирован на месте",
            vars={"i": i, "сравнений": comps, "обменов": swaps},
        )
        if not swapped:
            break
    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps, "обменов": swaps})


def selection(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    comps = 0
    swaps = 0
    done: tuple[int, ...] = ()
    yield Step(a[:], (), (), message="Начало сортировки выбором", vars={"сравнений": 0, "обменов": 0})
    for i in range(n - 1):
        m = i
        yield Step(
            a[:],
            (i,),
            done,
            pointers={"i": i, "min": m},
            message=f"Ищем минимум на суффиксе с позиции {i}",
            vars={"i": i, "min": m, "сравнений": comps, "обменов": swaps},
        )
        for j in range(i + 1, n):
            comps += 1
            yield Step(
                a[:],
                (m, j),
                done,
                pointers={"i": i, "min": m, "j": j},
                message=f"Сравнение текущего минимума A[{m}]={a[m]} и A[{j}]={a[j]}",
                vars={"i": i, "min": m, "j": j, "сравнений": comps, "обменов": swaps},
            )
            if a[j] < a[m]:
                m = j
                yield Step(
                    a[:],
                    (m,),
                    done,
                    pointers={"i": i, "min": m},
                    message=f"Найден новый минимум: A[{m}]={a[m]}",
                    vars={"i": i, "min": m, "j": j, "сравнений": comps, "обменов": swaps},
                )
        if m != i:
            a[i], a[m] = a[m], a[i]
            swaps += 1
            yield Step(
                a[:],
                (i, m),
                done,
                pointers={"i": i},
                message=f"Перенос минимума: ставим {a[i]} на индекс {i}",
                vars={"i": i, "min": m, "сравнений": comps, "обменов": swaps},
            )
        done += (i,)
        yield Step(
            a[:],
            (),
            done,
            message=f"Позиция {i} зафиксирована: {a[i]}",
            vars={"i": i, "сравнений": comps, "обменов": swaps},
        )
    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps, "обменов": swaps})


def insertion(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    comps = 0
    shifts = 0
    yield Step(a[:], (), (0,), message="Начало сортировки вставками", vars={"сравнений": 0, "сдвигов": 0})
    for i in range(1, n):
        key = a[i]
        j = i - 1
        yield Step(
            a[:],
            (i,),
            tuple(range(i)),
            pointers={"i": i, "key": i},
            message=f"Вставляем элемент A[{i}]={key} в отсортированную часть",
            vars={"i": i, "key": key, "сравнений": comps, "сдвигов": shifts},
        )
        while j >= 0:
            comps += 1
            yield Step(
                a[:],
                (j, j + 1),
                tuple(range(i)),
                pointers={"j": j},
                message=f"Сравнение A[{j}]={a[j]} с ключом {key}",
                vars={"i": i, "j": j, "key": key, "сравнений": comps, "сдвигов": shifts},
            )
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                yield Step(
                    a[:],
                    (j + 1,),
                    tuple(range(i)),
                    pointers={"j": j},
                    message=f"Сдвиг {a[j + 1]} вправо на позицию {j + 1}",
                    vars={"i": i, "j": j, "key": key, "сравнений": comps, "сдвигов": shifts},
                )
                j -= 1
            else:
                break
        a[j + 1] = key
        yield Step(
            a[:],
            (j + 1,),
            tuple(range(i + 1)),
            pointers={"вставка": j + 1},
            message=f"Ключ {key} размещён на позиции {j + 1}",
            vars={"i": i, "key": key, "сравнений": comps, "сдвигов": shifts},
        )
    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps, "сдвигов": shifts})


def two_pointers(values: list[int], target: int) -> Iterator[Step]:
    a = sorted(values)
    n = len(a)
    if n == 0:
        return
    left = 0
    right = n - 1
    yield Step(
        a[:],
        (left, right),
        (),
        pointers={"L": left, "R": right},
        message=f"Два указателя: поиск пары с суммой {target}",
        vars={"L": left, "R": right, "цель": target},
    )
    while left < right:
        curr_sum = a[left] + a[right]
        yield Step(
            a[:],
            (left, right),
            (),
            pointers={"L": left, "R": right},
            message=f"Сумма A[{left}]({a[left]}) + A[{right}]({a[right]}) = {curr_sum} (цель {target})",
            vars={"L": left, "R": right, "A[L]": a[left], "A[R]": a[right], "сумма": curr_sum, "цель": target},
        )
        if curr_sum == target:
            yield Step(
                a[:],
                (),
                (left, right),
                pointers={"L": left, "R": right},
                message=f"Пара найдена: {a[left]} + {a[right]} = {target} на индексах {left} и {right}!",
                vars={"L": left, "R": right, "сумма": curr_sum, "найдено": True},
            )
            return
        elif curr_sum < target:
            yield Step(
                a[:],
                (left,),
                (),
                pointers={"L": left, "R": right},
                message=f"{curr_sum} < {target} (сумма мала) → сдвигаем L вправо",
                vars={"L": left + 1, "R": right, "цель": target},
            )
            left += 1
        else:
            yield Step(
                a[:],
                (right,),
                (),
                pointers={"L": left, "R": right},
                message=f"{curr_sum} > {target} (сумма велика) → сдвигаем R влево",
                vars={"L": left, "R": right - 1, "цель": target},
            )
            right -= 1

    yield Step(
        a[:],
        (),
        (),
        message=f"Пара с суммой {target} не найдена",
        vars={"цель": target, "найдено": False},
    )


def prefix_sums(values: list[int], query_range: str = "2 5") -> Iterator[Step]:
    a = list(values)
    n = len(a)
    if n == 0:
        return
    p = [0] * n
    yield Step(a[:], (), (), message=f"Исходный массив A: {a}", vars={"длина": n})
    running = 0
    for i in range(n):
        prev = running
        running += a[i]
        p[i] = running
        yield Step(
            p[:],
            (i,),
            tuple(range(i)),
            pointers={"i": i},
            message=f"P[{i}] = {prev} + A[{i}]({a[i]}) = {running}",
            vars={"i": i, "A[i]": a[i], "P[i]": running},
        )

    parts = [int(x) for x in query_range.replace(",", " ").split() if x.strip()]
    ql = max(0, min(parts[0] if len(parts) > 0 else 1, n - 1))
    qr = max(ql, min(parts[1] if len(parts) > 1 else max(1, n - 2), n - 1))

    ans = p[qr] - (p[ql - 1] if ql > 0 else 0)
    prev_str = f"P[{ql - 1}]({p[ql - 1]})" if ql > 0 else "0"
    yield Step(
        p[:],
        tuple(range(ql, qr + 1)),
        tuple(range(n)),
        pointers={"L": ql, "R": qr},
        message=f"Запрос суммы [{ql}..{qr}]: P[{qr}]({p[qr]}) - {prev_str} = {ans}",
        vars={"L": ql, "R": qr, "P[R]": p[qr], "сумма": ans},
    )


def binary_search(values: list[int], target: int) -> Iterator[Step]:
    a = sorted(values)
    left = 0
    right = len(a) - 1
    checks = 0
    yield Step(
        a[:],
        (),
        (),
        pointers={"L": left, "R": right},
        message=f"Поиск числа {target} в отсортированном массиве",
        vars={"target": target, "L": left, "R": right, "проверок": 0},
    )
    while left <= right:
        mid = (left + right) // 2
        checks += 1
        yield Step(
            a[:],
            (mid,),
            (),
            pointers={"L": left, "M": mid, "R": right},
            message=f"Проверка середины: A[{mid}] = {a[mid]} vs {target}",
            vars={"target": target, "mid": mid, "значение": a[mid], "проверок": checks},
        )
        if a[mid] == target:
            yield Step(
                a[:],
                (),
                (mid,),
                pointers={"M": mid},
                message=f"Элемент {target} найден на индексе {mid}!",
                vars={"target": target, "индекс": mid, "проверок": checks, "найден": True},
            )
            return
        elif a[mid] < target:
            yield Step(
                a[:],
                (),
                (),
                pointers={"L": mid + 1, "R": right},
                message=f"{a[mid]} < {target} → отсекаем левую часть [{left}..{mid}]",
                vars={"target": target, "новый L": mid + 1, "R": right, "проверок": checks},
            )
            left = mid + 1
        else:
            yield Step(
                a[:],
                (),
                (),
                pointers={"L": left, "R": mid - 1},
                message=f"{a[mid]} > {target} → отсекаем правую часть [{mid}..{right}]",
                vars={"target": target, "L": left, "новый R": mid - 1, "проверок": checks},
            )
            right = mid - 1

    yield Step(
        a[:],
        (),
        (),
        message=f"Число {target} отсутствует в массиве",
        vars={"target": target, "проверок": checks, "найден": False},
    )


def linear_search(values: list[int], target: int) -> Iterator[Step]:
    a = list(values)
    checks = 0
    yield Step(
        a[:],
        (),
        (),
        message=f"Линейный поиск числа {target} слева направо",
        vars={"target": target, "проверок": 0},
    )
    for i in range(len(a)):
        checks += 1
        yield Step(
            a[:],
            (i,),
            (),
            pointers={"i": i},
            message=f"Проверка позиции {i}: A[{i}]={a[i]} vs {target}",
            vars={"i": i, "значение": a[i], "target": target, "проверок": checks},
        )
        if a[i] == target:
            yield Step(
                a[:],
                (),
                (i,),
                pointers={"i": i},
                message=f"Элемент {target} найден на позиции {i}!",
                vars={"i": i, "target": target, "проверок": checks, "найден": True},
            )
            return

    yield Step(
        a[:],
        (),
        (),
        message=f"Число {target} не найдено",
        vars={"target": target, "проверок": checks, "найден": False},
    )


def coin_change(amount: int, coins: list[int]) -> Iterator[Step]:
    sorted_coins = sorted(coins, reverse=True)
    rem = amount
    chosen: list[int] = []
    yield Step(
        chosen[:],
        (),
        (),
        message=f"Жадный размен суммы {amount} монетами {sorted_coins}",
        vars={"сумма": amount, "остаток": rem, "монет": 0},
    )
    for c in sorted_coins:
        if c <= 0:
            continue
        count = rem // c
        yield Step(
            chosen[:],
            (),
            (),
            message=f"Номинал {c}: влезает {count} шт., остаток был {rem}",
            vars={"номинал": c, "взято": count, "остаток": rem},
        )
        if count > 0:
            for _ in range(count):
                chosen.append(c)
                rem -= c
                yield Step(
                    chosen[:],
                    (len(chosen) - 1,),
                    (),
                    message=f"+ монета {c} (остаток: {rem})",
                    vars={"добавлено": c, "остаток": rem, "всего_монет": len(chosen)},
                )

    status = "Сумма полностью разменена" if rem == 0 else f"Не удалось разменять {rem}"
    yield Step(
        chosen[:],
        (),
        tuple(range(len(chosen))),
        message=f"{status}: {len(chosen)} монет",
        vars={"итого_монет": len(chosen), "остаток": rem, "номиналы": chosen},
    )
