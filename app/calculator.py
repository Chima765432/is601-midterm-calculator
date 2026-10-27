"""Facade: one Calculator class in front of operations, history, undo, and config."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.history import CalculationHistory
from app.input_validators import validate_number
from app.logger import Logger

logger = Logger.get(__name__)


class Calculator:
    """The single interface the REPL uses."""

    def __init__(self, config=None):
        self.config = config or CalculatorConfig.from_env()
        self.history = CalculationHistory(self.config.max_history_size, self.config.encoding)
        self._observers = []
        self._undo_stack = []
        self._redo_stack = []

    def attach(self, observer):
        self._observers.append(observer)

    def calculate(self, operation, a, b):
        """Validate the input, run the operation, record it, and notify observers."""
        limit = self.config.max_input_value
        calculation = Calculation.create(
            operation, validate_number(a, limit), validate_number(b, limit), self.config.precision
        )
        self._remember()
        self.history.add(calculation)
        for observer in self._observers:
            observer.on_calculation(calculation)
        return calculation.result

    def _remember(self):
        """Save the current history for undo; any new change ends the redo chain."""
        self._undo_stack.append(CalculatorMemento(self.history.frame))
        self._redo_stack.clear()

    def undo(self):
        return self._step(self._undo_stack, self._redo_stack)

    def redo(self):
        return self._step(self._redo_stack, self._undo_stack)

    def _step(self, source, target):
        """Move one snapshot between the undo and redo stacks."""
        if not source:
            return False
        target.append(CalculatorMemento(self.history.frame))
        self.history.frame = source.pop().restore()
        return True

    def clear(self):
        """Empty the history. This can be undone."""
        self._remember()
        self.history.clear()
        logger.info("History cleared")

    def save(self):
        self.history.save(self.config.history_file)
        logger.info("History saved to %s", self.config.history_file)

    def load(self):
        loaded = self.history.load(self.config.history_file)
        if loaded:
            logger.info("Loaded %d calculations from %s", len(self.history), self.config.history_file)
        else:
            logger.warning("No history file at %s", self.config.history_file)
        return loaded
