from typing import Callable, Iterator
from .steps import Step

DEFAULT_SORT = [14, 5, 22, 3, 11, 18, 8, 2, 9]
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


def quicksort(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    done: set[int] = set()
    comps = 0
    swaps = 0

    def qsort(low: int, high: int):
        nonlocal comps, swaps
        if low > high:
            return
        if low == high:
            done.add(low)
            yield Step(a[:], (low,), tuple(sorted(done)), message=f"Элемент {a[low]} на месте", vars={"сравнений": comps, "обменов": swaps})
            return

        pivot = a[high]
        yield Step(
            a[:],
            (high,),
            tuple(sorted(done)),
            pointers={"L": low, "R": high, "P": high},
            message=f"Опорный элемент A[{high}] = {pivot}",
            vars={"low": low, "high": high, "pivot": pivot, "сравнений": comps, "обменов": swaps},
        )

        i = low
        for j in range(low, high):
            comps += 1
            yield Step(
                a[:],
                (j, high),
                tuple(sorted(done)),
                pointers={"i": i, "j": j, "P": high},
                message=f"Сравнение A[{j}]={a[j]} с опорным {pivot}",
                vars={"i": i, "j": j, "pivot": pivot, "сравнений": comps, "обменов": swaps},
            )
            if a[j] < pivot:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    swaps += 1
                    yield Step(
                        a[:],
                        (i, j),
                        tuple(sorted(done)),
                        pointers={"i": i, "j": j, "P": high},
                        message=f"Обмен A[{i}] ⇄ A[{j}]: {a[j]} и {a[i]}",
                        vars={"i": i, "j": j, "сравнений": comps, "обменов": swaps},
                    )
                i += 1

        if i != high:
            a[i], a[high] = a[high], a[i]
            swaps += 1
            yield Step(
                a[:],
                (i, high),
                tuple(sorted(done)),
                pointers={"P": i},
                message=f"Ставим опорный {pivot} на итоговую позицию {i}",
                vars={"сравнений": comps, "обменов": swaps},
            )

        done.add(i)
        yield Step(
            a[:],
            (),
            tuple(sorted(done)),
            pointers={"P": i},
            message=f"Опорный {pivot} зафиксирован на позиции {i}",
            vars={"сравнений": comps, "обменов": swaps},
        )

        yield from qsort(low, i - 1)
        yield from qsort(i + 1, high)

    yield Step(a[:], (), (), message="Начало быстрой сортировки", vars={"сравнений": 0, "обменов": 0})
    yield from qsort(0, n - 1)
    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps, "обменов": swaps})


def mergesort(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    comps = 0

    def msort(left: int, right: int):
        nonlocal comps
        if left >= right:
            return
        mid = (left + right) // 2
        yield Step(
            a[:],
            (mid,),
            (),
            pointers={"L": left, "M": mid, "R": right},
            message=f"Деление отрезка [{left}..{right}] на [{left}..{mid}] и [{mid + 1}..{right}]",
            vars={"left": left, "mid": mid, "right": right, "сравнений": comps},
        )
        yield from msort(left, mid)
        yield from msort(mid + 1, right)

        merged = []
        i, j = left, mid + 1
        yield Step(
            a[:],
            tuple(range(left, right + 1)),
            (),
            pointers={"i": i, "j": j},
            message=f"Слияние подмассивов [{left}..{mid}] и [{mid + 1}..{right}]",
            vars={"i": i, "j": j, "сравнений": comps},
        )

        while i <= mid and j <= right:
            comps += 1
            yield Step(
                a[:],
                (i, j),
                (),
                pointers={"i": i, "j": j},
                message=f"Сравнение A[{i}]={a[i]} и A[{j}]={a[j]}",
                vars={"i": i, "j": j, "сравнений": comps},
            )
            if a[i] <= a[j]:
                merged.append(a[i])
                i += 1
            else:
                merged.append(a[j])
                j += 1

        while i <= mid:
            merged.append(a[i])
            i += 1
        while j <= right:
            merged.append(a[j])
            j += 1

        for idx, val in enumerate(merged):
            a[left + idx] = val
            yield Step(
                a[:],
                (left + idx,),
                (),
                pointers={"pos": left + idx},
                message=f"Запись в основной массив: A[{left + idx}] = {val}",
                vars={"left": left, "right": right, "сравнений": comps},
            )

    yield Step(a[:], (), (), message="Начало сортировки слиянием", vars={"сравнений": 0})
    yield from msort(0, n - 1)
    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps})


def shaker(values: list[int]) -> Iterator[Step]:
    a = list(values)
    n = len(a)
    comps = 0
    swaps = 0
    left = 0
    right = n - 1
    done: set[int] = set()
    yield Step(a[:], (), (), message="Начало шейкерной сортировки", vars={"сравнений": 0, "обменов": 0})
    while left < right:
        swapped = False
        for i in range(left, right):
            comps += 1
            yield Step(
                a[:],
                (i, i + 1),
                tuple(sorted(done)),
                pointers={"i": i},
                message=f"Проход вправо: сравнение A[{i}]={a[i]} и A[{i + 1}]={a[i + 1]}",
                vars={"направление": "вправо", "сравнений": comps, "обменов": swaps},
            )
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swaps += 1
                swapped = True
                yield Step(
                    a[:],
                    (i, i + 1),
                    tuple(sorted(done)),
                    pointers={"i": i},
                    message=f"Обмен: {a[i + 1]} ⇄ {a[i]}",
                    vars={"направление": "вправо", "сравнений": comps, "обменов": swaps},
                )
        done.add(right)
        right -= 1
        if not swapped:
            break

        swapped = False
        for i in range(right, left, -1):
            comps += 1
            yield Step(
                a[:],
                (i - 1, i),
                tuple(sorted(done)),
                pointers={"i": i},
                message=f"Проход влево: сравнение A[{i - 1}]={a[i - 1]} и A[{i}]={a[i]}",
                vars={"направление": "влево", "сравнений": comps, "обменов": swaps},
            )
            if a[i - 1] > a[i]:
                a[i - 1], a[i] = a[i], a[i - 1]
                swaps += 1
                swapped = True
                yield Step(
                    a[:],
                    (i - 1, i),
                    tuple(sorted(done)),
                    pointers={"i": i},
                    message=f"Обмен: {a[i]} ⇄ {a[i - 1]}",
                    vars={"направление": "влево", "сравнений": comps, "обменов": swaps},
                )
        done.add(left)
        left += 1
        if not swapped:
            break

    yield Step(a[:], (), tuple(range(n)), message="Массив полностью отсортирован", vars={"сравнений": comps, "обменов": swaps})


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
