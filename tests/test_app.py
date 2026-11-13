import asyncio

from algoss.algorithms import PROGRAMS
from algoss.app import Algoss


def test_sorts():
    for name in ("Пузырьковая", "Выбором"):
        steps = list(PROGRAMS["Сортировки"][name].run())
        assert steps[-1].array == sorted(steps[-1].array)


def test_basics():
    for name in ("Цикл for и if/else", "Цикл while"):
        program = PROGRAMS["Основы"][name]
        steps = list(program.run())
        assert steps[-1].line is not None
        for step in steps:
            assert 0 <= step.line < len(program.code)


def test_coins():
    steps = list(PROGRAMS["Жадные"]["Размен монетами"].run())
    assert sum(steps[-1].array) == 137


def test_app():
    async def run():
        app = Algoss()
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.press("right")
            await pilot.press("right")
            await pilot.press("space")
            await pilot.pause(0.1)
            await pilot.press("space")
            assert not app.playing
            app.query_one("#cat").value = "Жадные"
            await pilot.pause()
            assert app.query_one("#algo").value == "Размен монетами"
            await pilot.click("#step")
            await pilot.click("#play")
            await pilot.pause(0.1)
            await pilot.click("#play")
            assert not app.playing
            await pilot.press("r")
            assert app.steps == 1

    asyncio.run(run())
