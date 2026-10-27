import logging

import pytest

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.history import AutoSaveObserver, CalculationHistory, LoggingObserver


def make(result):
    return Calculation("add", 1.0, 1.0, float(result))


@pytest.mark.parametrize("count, max_size, kept", [(1, 5, 1), (5, 5, 5), (7, 3, 3)])
def test_add_respects_max_size(count, max_size, kept):
    history = CalculationHistory(max_size)
    for number in range(count):
        history.add(make(number))
    assert len(history) == kept
    assert history.entries()[-1].result == count - 1


def test_clear():
    history = CalculationHistory(5)
    history.add(make(1))
    history.clear()
    assert len(history) == 0


def test_save_creates_folder_and_load_reads_it_back(tmp_path):
    path = tmp_path / "nested" / "history.csv"
    history = CalculationHistory(5)
    history.add(make(4))
    history.save(path)
    loaded = CalculationHistory(5)
    assert loaded.load(path) is True
    assert loaded.entries()[0].result == 4.0


def test_csv_has_the_required_columns(tmp_path):
    path = tmp_path / "history.csv"
    history = CalculationHistory(5)
    history.add(make(1))
    history.save(path)
    assert path.read_text().splitlines()[0] == "operation,a,b,result,timestamp"


def test_load_missing_file(tmp_path):
    assert CalculationHistory(5).load(tmp_path / "none.csv") is False


@pytest.mark.parametrize("content", [
    "",
    "operation,a,b\nadd,1,2\n",
    "operation,a,b,result,timestamp\nadd,one,2,3,2026-01-01T00:00:00\n",
    'operation,a,b,result,timestamp\n"add,1,2,3\n',
])
def test_load_rejects_malformed_files(tmp_path, content):
    path = tmp_path / "history.csv"
    path.write_text(content)
    with pytest.raises(HistoryError):
        CalculationHistory(5).load(path)


def test_save_failure_raises_history_error(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("not a folder")
    with pytest.raises(HistoryError):
        CalculationHistory(5).save(blocker / "history.csv")


def test_logging_observer(caplog):
    with caplog.at_level(logging.INFO):
        LoggingObserver().on_calculation(make(2))
    assert "operation=add a=1.0 b=1.0 result=2.0" in caplog.text


@pytest.mark.parametrize("auto_save, should_exist", [(True, True), (False, False)])
def test_auto_save_observer(calculator, auto_save, should_exist):
    calculator.config.auto_save = auto_save
    AutoSaveObserver(calculator).on_calculation(make(1))
    assert calculator.config.history_file.exists() is should_exist
