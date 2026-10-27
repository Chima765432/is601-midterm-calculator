"""Memento pattern: saved copies of the history for undo and redo."""


class CalculatorMemento:
    """Holds a copy of the history table at one point in time."""

    def __init__(self, frame):
        self._frame = frame.copy()

    def restore(self):
        """Return a copy of the saved table."""
        return self._frame.copy()
