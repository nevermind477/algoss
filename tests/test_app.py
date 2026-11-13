import asyncio

from algoss.algorithms import (
    DEFAULT_COINS,
    binary_search,
    bubble,
    coin_change,
    insertion,
    linear_search,
    prefix_sums,
    selection,
    two_pointers,
)
from algoss.app import Algoss


def test_sorts():
    arr = [9, 3, 7, 1, 5, 4, 8, 2]
    expected = sorted(arr)
    for fn in (bubble, selection, insertion):
        steps = list(fn(arr))
        assert steps[-1].array == expected


def test_arrays():
    arr = [2, 4, 7, 11, 15, 19, 24, 30]
    steps_tp = list(two_pointers(arr, 26))
    assert steps_tp[-1].vars.get("найдено") is True

    steps_ps = list(prefix_sums([3, 2, 5, 1, 4, 3], "1 4"))
    assert steps_ps[-1].array == [3, 5, 10, 11, 15, 18]
    assert steps_ps[-1].vars.get("сумма") == 12


def test_searches():
    arr = [2, 5, 8, 12, 16, 23, 38]
    bs_found = list(binary_search(arr, 12))
    assert bs_found[-1].vars.get("найден") is True

    bs_missing = list(binary_search(arr, 99))
    assert bs_missing[-1].vars.get("найден") is False

    ls_found = list(linear_search(arr, 8))
    assert ls_found[-1].vars.get("найден") is True


def test_coins():
    steps = list(coin_change(137, DEFAULT_COINS))
    assert sum(steps[-1].array) == 137


def test_app_vim_navigation():
    async def run():
        app = Algoss()
        async with app.run_test(size=(80, 24)) as pilot:
            # 1. Test step with 'n'
            assert app.steps == 1
            await pilot.press("n")
            assert app.steps == 2

            # 2. Test play / pause with 'space'
            await pilot.press("space")
            assert app.playing
            await pilot.pause(0.05)
            await pilot.press("space")
            assert not app.playing

            # 3. Test reset with 'r'
            await pilot.press("r")
            assert app.steps == 1

            # 4. Test algorithm navigation with 'j' and 'k'
            assert app.current_algo == "Пузырьковая"
            await pilot.press("j")
            assert app.current_algo == "Выбором"
            await pilot.press("j")
            assert app.current_algo == "Вставками"
            await pilot.press("k")
            assert app.current_algo == "Выбором"

            # 5. Test category switching with 'l' and 'h'
            assert app.current_cat == "Сортировки"
            await pilot.press("l")
            assert app.current_cat == "Массивы"
            assert app.current_algo == "Два указателя"
            await pilot.press("j")
            assert app.current_algo == "Префиксные суммы"
            await pilot.press("l")
            assert app.current_cat == "Поиск"
            assert app.current_algo == "Бинарный поиск"
            await pilot.press("l")
            assert app.current_cat == "Жадные"
            assert app.current_algo == "Размен монет"
            await pilot.press("h")
            assert app.current_cat == "Поиск"

            # 6. Test direct category keys '1', '2', '3', '4'
            await pilot.press("1")
            assert app.current_cat == "Сортировки"
            await pilot.press("2")
            assert app.current_cat == "Массивы"
            await pilot.press("4")
            assert app.current_cat == "Жадные"
            await pilot.press("3")
            assert app.current_cat == "Поиск"

            # 7. Test randomize with 'g'
            await pilot.press("g")
            assert app.steps == 1

            # 8. Test edit mode with 'i' and input submit
            await pilot.press("i")
            assert app.mode == "INSERT"
            inp1 = app.query_one("#input_p1")
            inp1.value = "10, 20, 30, 40"
            await pilot.press("enter")
            assert app.mode == "NORMAL"
            assert "10" in app.current_p1

            # 9. Test speed change with '+' and '-'
            old_speed = app.speed
            await pilot.press("plus")
            assert app.speed == old_speed + 10
            await pilot.press("minus")
            assert app.speed == old_speed

    asyncio.run(run())
