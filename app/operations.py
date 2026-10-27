"""Arithmetic operations, using the Strategy, Factory, and Decorator patterns."""

from abc import ABC, abstractmethod

from app.exceptions import OperationError


class Operation(ABC):
    """Strategy interface: every operation computes a result from two numbers."""

    name = ""
    description = ""

    @abstractmethod
    def compute(self, a, b):
        """Return the result of the operation."""
        raise NotImplementedError  # pragma: no cover


class OperationFactory:
    """Builds the operation that matches a name.

    Operations add themselves through the register decorator, so the factory
    and the help menu both come from the same registry.
    """

    _operations = {}

    @classmethod
    def register(cls, name, description):
        def decorator(operation_class):
            operation_class.name = name
            operation_class.description = description
            cls._operations[name] = operation_class
            return operation_class
        return decorator

    @classmethod
    def create(cls, name):
        operation = cls._operations.get(name)
        if operation is None:
            raise OperationError(f"Unknown operation: {name}")
        return operation()

    @classmethod
    def names(cls):
        return list(cls._operations)

    @classmethod
    def descriptions(cls):
        """Return (name, description) pairs for the help menu."""
        return [(name, op.description) for name, op in cls._operations.items()]


def _require_nonzero(b, message):
    # LBYL: check the second operand before using it as a divisor.
    if b == 0:
        raise OperationError(message)


@OperationFactory.register("add", "a + b")
class Add(Operation):
    def compute(self, a, b):
        return a + b


@OperationFactory.register("subtract", "a - b")
class Subtract(Operation):
    def compute(self, a, b):
        return a - b


@OperationFactory.register("multiply", "a * b")
class Multiply(Operation):
    def compute(self, a, b):
        return a * b


@OperationFactory.register("divide", "a / b")
class Divide(Operation):
    def compute(self, a, b):
        _require_nonzero(b, "Cannot divide by zero")
        return a / b


@OperationFactory.register("power", "a raised to the power b")
class Power(Operation):
    def compute(self, a, b):
        if a == 0 and b < 0:
            raise OperationError("Zero cannot be raised to a negative power")
        if a < 0 and not float(b).is_integer():
            raise OperationError("A negative number cannot be raised to a fractional power")
        return a ** b


@OperationFactory.register("root", "the b-th root of a")
class Root(Operation):
    def compute(self, a, b):
        _require_nonzero(b, "The root degree cannot be zero")
        if a < 0:
            # An odd whole-number root of a negative number is real; others are not.
            if not (float(b).is_integer() and int(b) % 2 == 1):
                raise OperationError("Only odd roots of a negative number are defined")
            return -((-a) ** (1 / b))
        return a ** (1 / b)


@OperationFactory.register("modulus", "remainder of a / b")
class Modulus(Operation):
    def compute(self, a, b):
        _require_nonzero(b, "Cannot take the modulus with zero")
        return a % b


@OperationFactory.register("int_divide", "a / b with the fraction discarded")
class IntDivide(Operation):
    def compute(self, a, b):
        _require_nonzero(b, "Cannot divide by zero")
        return float(int(a / b))


@OperationFactory.register("percent", "a as a percentage of b")
class Percent(Operation):
    def compute(self, a, b):
        _require_nonzero(b, "Cannot take a percentage of zero")
        return a / b * 100


@OperationFactory.register("abs_diff", "absolute difference of a and b")
class AbsDiff(Operation):
    def compute(self, a, b):
        return abs(a - b)
