import pytest

from app.exceptions import ValidationError
from app.input_validators import validate_number


@pytest.mark.parametrize("value, expected", [("2", 2.0), (" 3.5 ", 3.5), ("-4", -4.0), (7, 7.0), ("100", 100.0)])
def test_valid_numbers(value, expected):
    assert validate_number(value, 100) == expected


@pytest.mark.parametrize("value", ["abc", "", None, "1,5", "nan", "inf", "101", "-101"])
def test_invalid_numbers(value):
    with pytest.raises(ValidationError):
        validate_number(value, 100)
