import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig


@pytest.fixture
def config(tmp_path):
    return CalculatorConfig(
        log_dir=tmp_path / "logs", history_dir=tmp_path / "history", auto_save=False
    )


@pytest.fixture
def calculator(config):
    return Calculator(config)
