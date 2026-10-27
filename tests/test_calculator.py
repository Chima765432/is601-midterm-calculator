import pytest

from app.calculator import Calculator
from app.exceptions import HistoryError, OperationError, ValidationError


@pytest.mark.parametrize("operation, a, b, expected", [
    ("add", "2", "3", 5),
    ("power", "2", "10", 1024),
    ("modulus", "17", "5", 2),
    ("percent", "1", "8", 12.5),
])
def test_calculate(calculator, operation, a, b, expected):
    assert calculator.calculate(operation, a, b) == expected
    assert len(calculator.history) == 1


@pytest.mark.parametrize("operation, a, b, error", [
    ("add", "two", "3", ValidationError),
    ("add", "1", "1e13", ValidationError),
    ("divide", "1", "0", OperationError),
    ("sqrt", "1", "2", OperationError),
])
def test_failed_calculation_is_not_recorded(calculator, operation, a, b, error):
    with pytest.raises(error):
        calculator.calculate(operation, a, b)
    assert len(calculator.history) == 0


def test_undo_and_redo(calculator):
    calculator.calculate("add", "1", "1")
    calculator.calculate("add", "2", "2")
    assert calculator.undo() is True
    assert len(calculator.history) == 1
    assert calculator.redo() is True
    assert len(calculator.history) == 2


def test_nothing_to_undo_or_redo(calculator):
    assert calculator.undo() is False
    assert calculator.redo() is False


def test_new_calculation_clears_redo(calculator):
    calculator.calculate("add", "1", "1")
    calculator.undo()
    calculator.calculate("add", "5", "5")
    assert calculator.redo() is False


def test_clear_can_be_undone(calculator):
    calculator.calculate("add", "1", "1")
    calculator.clear()
    assert len(calculator.history) == 0
    calculator.undo()
    assert len(calculator.history) == 1


def test_save_and_load(calculator):
    calculator.calculate("multiply", "3", "4")
    calculator.save()
    calculator.clear()
    assert calculator.load() is True
    assert calculator.history.entries()[0].result == 12.0


def test_load_without_file(calculator):
    assert calculator.load() is False


def test_load_malformed_file_raises(calculator):
    calculator.config.history_file.parent.mkdir(parents=True)
    calculator.config.history_file.write_text("nonsense\n")
    with pytest.raises(HistoryError):
        calculator.load()


def test_default_config_comes_from_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "7")
    assert Calculator().config.max_history_size == 7
