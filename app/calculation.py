"""A single calculation and its conversion to and from a table row."""

from datetime import datetime

from app.operations import OperationFactory


class Calculation:
    """One calculation: the operation, both operands, the result, and when it ran."""

    COLUMNS = ["operation", "a", "b", "result", "timestamp"]

    def __init__(self, operation, a, b, result, timestamp=None):
        self.operation = operation
        self.a = a
        self.b = b
        self.result = result
        self.timestamp = timestamp or datetime.now()

    @classmethod
    def create(cls, operation, a, b, precision=4):
        """Run the named operation and return the finished calculation."""
        result = OperationFactory.create(operation).compute(a, b)
        return cls(operation, a, b, round(result, precision))

    def to_row(self):
        """Return the calculation as a dictionary for a DataFrame row."""
        return {
            "operation": self.operation,
            "a": self.a,
            "b": self.b,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_row(cls, row):
        """Rebuild a calculation from a DataFrame row."""
        return cls(
            row["operation"],
            float(row["a"]),
            float(row["b"]),
            float(row["result"]),
            datetime.fromisoformat(row["timestamp"]),
        )

    def __str__(self):
        return f"{self.operation}({self.a}, {self.b}) = {self.result}"
