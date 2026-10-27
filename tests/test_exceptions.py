import pytest

from app.exceptions import (
    CalculatorError, ConfigError, HistoryError, OperationError, ValidationError,
)


@pytest.mark.parametrize("error_class", [ValidationError, OperationError, ConfigError, HistoryError])
def test_each_error_is_a_calculator_error(error_class):
    with pytest.raises(CalculatorError, match="bad"):
        raise error_class("bad")
