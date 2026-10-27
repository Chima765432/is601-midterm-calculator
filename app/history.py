"""Calculation history stored in a pandas DataFrame, plus its observers."""

from abc import ABC, abstractmethod

import pandas as pd

from app.calculation import Calculation
from app.exceptions import HistoryError
from app.logger import Logger

logger = Logger.get(__name__)


class CalculationHistory:
    """Keeps calculations in a DataFrame and saves or loads them as CSV."""

    def __init__(self, max_size, encoding="utf-8"):
        self.max_size = max_size
        self.encoding = encoding
        self.frame = pd.DataFrame(columns=Calculation.COLUMNS)

    def add(self, calculation):
        row = pd.DataFrame([calculation.to_row()])
        frame = row if self.frame.empty else pd.concat([self.frame, row], ignore_index=True)
        self.frame = frame.tail(self.max_size).reset_index(drop=True)

    def entries(self):
        """Return the history as Calculation objects."""
        return [Calculation.from_row(row) for row in self.frame.to_dict("records")]

    def clear(self):
        self.frame = self.frame.iloc[0:0]

    def save(self, path):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.frame.to_csv(path, index=False, encoding=self.encoding)
        except OSError as error:
            raise HistoryError(f"Could not save history to {path}: {error}")

    def load(self, path):
        """Read the CSV if it exists. Returns False when there is no file.

        EAFP: try the read and turn each kind of bad file into a HistoryError.
        """
        try:
            frame = pd.read_csv(path, encoding=self.encoding)
        except FileNotFoundError:
            return False
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
            raise HistoryError(f"History file {path} could not be read: {error}")
        missing = set(Calculation.COLUMNS) - set(frame.columns)
        if missing:
            raise HistoryError(f"History file {path} is missing columns: {sorted(missing)}")
        try:
            [Calculation.from_row(row) for row in frame.to_dict("records")]
        except (TypeError, ValueError) as error:
            raise HistoryError(f"History file {path} has an invalid row: {error}")
        self.frame = frame[Calculation.COLUMNS].tail(self.max_size).reset_index(drop=True)
        return True

    def __len__(self):
        return len(self.frame)


class CalculationObserver(ABC):
    """Observer interface: notified after every calculation."""

    @abstractmethod
    def on_calculation(self, calculation):
        """React to a new calculation."""
        raise NotImplementedError  # pragma: no cover


class LoggingObserver(CalculationObserver):
    """Writes each calculation to the log file."""

    def on_calculation(self, calculation):
        logger.info(
            "Calculation: operation=%s a=%s b=%s result=%s",
            calculation.operation, calculation.a, calculation.b, calculation.result,
        )


class AutoSaveObserver(CalculationObserver):
    """Saves the history to CSV after each calculation when auto-save is on."""

    def __init__(self, calculator):
        self.calculator = calculator

    def on_calculation(self, calculation):
        if self.calculator.config.auto_save:
            self.calculator.save()
