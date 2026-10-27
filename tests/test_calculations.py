from datetime import datetime

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize("operation, a, b, precision, expected", [
    ("add", 1, 2, 4, 3),
    ("divide", 10, 3, 2, 3.33),
    ("root", 2, 2, 3, 1.414),
    ("percent", 1, 3, 1, 33.3),
])
def test_create_rounds_result(operation, a, b, precision, expected):
    assert Calculation.create(operation, a, b, precision).result == expected


def test_create_raises_for_unknown_operation():
    with pytest.raises(OperationError):
        Calculation.create("sqrt", 1, 2)


def test_row_round_trip():
    original = Calculation("power", 2.0, 3.0, 8.0, datetime(2026, 1, 1, 9, 30))
    restored = Calculation.from_row(original.to_row())
    assert (restored.operation, restored.a, restored.b, restored.result) == ("power", 2.0, 3.0, 8.0)
    assert restored.timestamp == original.timestamp


def test_str():
    assert str(Calculation("add", 2.0, 3.0, 5.0)) == "add(2.0, 3.0) = 5.0"
