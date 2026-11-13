import asyncio

from algoss.algorithms import (
    DEFAULT_COINS,
    DEFAULT_SORT,
    binary_search,
    bubble,
    coin_change,
    insertion,
    linear_search,
    mergesort,
    quicksort,
    selection,
    shaker,
)
from algoss.app import Algoss


def test_sorts():
    arr = [9, 3, 7, 1, 5, 4, 8, 2]
    expected = sorted(arr)
    for fn in (bubble, selection, insertion, quicksort, mergesort, shaker):
        steps = list(fn(arr))
        assert steps[-1].array == expected


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


def test_app():
    async def run():
        app = Algoss()
        async with app.run_test(size=(110, 34)) as pilot:
            await pilot.press("right")
            await pilot.press("right")
            await pilot.press("space")
            await pilot.pause(0.1)
            await pilot.press("space")
            assert not app.playing

            app.query_one("#cat").value = "Поиск"
            await pilot.pause()
            assert app.query_one("#algo").value == "Бинарный поиск"

            await pilot.click("#btn_rand")
            await pilot.pause()
            assert app.steps == 1

            app.query_one("#p2").value = "999"
            await pilot.click("#btn_apply")
            await pilot.pause()
            assert app.steps == 1

            app.query_one("#cat").value = "Жадные"
            await pilot.pause()
            assert app.query_one("#algo").value == "Размен монет"
            await pilot.click("#step")
            assert app.steps == 2

            await pilot.press("r")
            assert app.steps == 1

    asyncio.run(run())
