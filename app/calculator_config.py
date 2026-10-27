"""Settings loaded from a .env file and environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigError

TRUE_VALUES = ("true", "1", "yes")
FALSE_VALUES = ("false", "0", "no")


@dataclass
class CalculatorConfig:
    """The calculator's settings, checked as soon as they are created."""

    log_dir: Path = Path("logs")
    history_dir: Path = Path("history")
    max_history_size: int = 100
    auto_save: bool = True
    precision: int = 4
    max_input_value: float = 1e12
    encoding: str = "utf-8"
    log_file: Path = None
    history_file: Path = None

    def __post_init__(self):
        self.log_dir = Path(self.log_dir)
        self.history_dir = Path(self.history_dir)
        self.log_file = Path(self.log_file) if self.log_file else self.log_dir / "calculator.log"
        self.history_file = (
            Path(self.history_file) if self.history_file else self.history_dir / "history.csv"
        )
        if self.max_history_size < 1:
            raise ConfigError("CALCULATOR_MAX_HISTORY_SIZE must be at least 1")
        if self.precision < 0:
            raise ConfigError("CALCULATOR_PRECISION cannot be negative")
        if self.max_input_value <= 0:
            raise ConfigError("CALCULATOR_MAX_INPUT_VALUE must be positive")
        try:
            "".encode(self.encoding)
        except LookupError:
            raise ConfigError(f"Unknown encoding: {self.encoding}")

    @classmethod
    def from_env(cls, env_file=".env"):
        """Load the .env file, then build the config from the environment."""
        load_dotenv(env_file)
        return cls(
            log_dir=os.getenv("CALCULATOR_LOG_DIR", "logs"),
            history_dir=os.getenv("CALCULATOR_HISTORY_DIR", "history"),
            max_history_size=_read_number("CALCULATOR_MAX_HISTORY_SIZE", 100, int),
            auto_save=_read_bool("CALCULATOR_AUTO_SAVE", True),
            precision=_read_number("CALCULATOR_PRECISION", 4, int),
            max_input_value=_read_number("CALCULATOR_MAX_INPUT_VALUE", 1e12, float),
            encoding=os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8"),
            log_file=os.getenv("CALCULATOR_LOG_FILE"),
            history_file=os.getenv("CALCULATOR_HISTORY_FILE"),
        )


def _read_number(name, default, convert):
    try:
        return convert(os.getenv(name, default))
    except ValueError:
        raise ConfigError(f"{name} must be a number")


def _read_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true or false")
