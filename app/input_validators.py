"""Checks applied to user input before it reaches an operation."""

import math

from app.exceptions import ValidationError


def validate_number(value, max_value):
    """Convert value to a float within the allowed range.

    EAFP: try the conversion and handle the failure. LBYL: then check for
    nan, infinity, and values larger than the configured maximum.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"'{value}' is not a number")
    if math.isnan(number) or math.isinf(number):
        raise ValidationError(f"'{value}' is not a finite number")
    if abs(number) > max_value:
        raise ValidationError(f"{value} is larger than the maximum of {max_value:g}")
    return number
