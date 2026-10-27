"""Exceptions raised by the calculator."""


class CalculatorError(Exception):
    """Parent of every calculator error, so the REPL can catch them in one place."""


class ValidationError(CalculatorError):
    """Raised when input cannot be used as a number or is out of range."""


class OperationError(CalculatorError):
    """Raised when an operation is unknown or has no valid result."""


class ConfigError(CalculatorError):
    """Raised when a setting in the environment is invalid."""


class HistoryError(CalculatorError):
    """Raised when the history file cannot be read or written."""
