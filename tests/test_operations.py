import pytest

from app.exceptions import OperationError
from app.operations import Operation, OperationFactory


@pytest.mark.parametrize("name, a, b, expected", [
    ("add", 2, 3, 5),
    ("subtract", 2, 3, -1),
    ("multiply", -4, 3, -12),
    ("divide", 7, 2, 3.5),
    ("power", 2, -1, 0.5),
    ("power", -2, 3, -8),
    ("root", 27, 3, 3),
    ("root", -8, 3, -2),
    ("modulus", 10, 3, 1),
    ("modulus", 7.5, 2, 1.5),
    ("int_divide", 7, 2, 3),
    ("int_divide", -7, 2, -3),
    ("percent", 25, 200, 12.5),
    ("abs_diff", 3, 10, 7),
    ("abs_diff", -3, 3, 6),
])
def test_operations(name, a, b, expected):
    assert OperationFactory.create(name).compute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("name, a, b", [
    ("divide", 5, 0),
    ("power", 0, -2),
    ("power", -8, 0.5),
    ("root", 9, 0),
    ("root", -16, 2),
    ("root", -8, 1.5),
    ("modulus", 5, 0),
    ("int_divide", 5, 0),
    ("percent", 5, 0),
])
def test_invalid_operations(name, a, b):
    with pytest.raises(OperationError):
        OperationFactory.create(name).compute(a, b)


def test_all_ten_operations_are_registered():
    assert OperationFactory.names() == [
        "add", "subtract", "multiply", "divide", "power",
        "root", "modulus", "int_divide", "percent", "abs_diff",
    ]


def test_factory_returns_operation_objects():
    for name in OperationFactory.names():
        assert isinstance(OperationFactory.create(name), Operation)


def test_registering_a_new_operation_updates_the_menu():
    @OperationFactory.register("double_sum", "2 * (a + b)")
    class DoubleSum(Operation):
        def compute(self, a, b):
            return 2 * (a + b)

    try:
        assert ("double_sum", "2 * (a + b)") in OperationFactory.descriptions()
        assert OperationFactory.create("double_sum").compute(1, 2) == 6
    finally:
        del OperationFactory._operations["double_sum"]


def test_factory_rejects_unknown_name():
    with pytest.raises(OperationError):
        OperationFactory.create("sqrt")
