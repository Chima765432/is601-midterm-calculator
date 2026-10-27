from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigError

VARIABLES = (
    "CALCULATOR_LOG_DIR", "CALCULATOR_HISTORY_DIR", "CALCULATOR_MAX_HISTORY_SIZE",
    "CALCULATOR_AUTO_SAVE", "CALCULATOR_PRECISION", "CALCULATOR_MAX_INPUT_VALUE",
    "CALCULATOR_DEFAULT_ENCODING", "CALCULATOR_LOG_FILE", "CALCULATOR_HISTORY_FILE",
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)


def test_defaults_when_nothing_is_set():
    config = CalculatorConfig.from_env(env_file="missing.env")
    assert config == CalculatorConfig()
    assert config.log_file == Path("logs/calculator.log")
    assert config.history_file == Path("history/history.csv")


def test_reads_values_from_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CALCULATOR_LOG_DIR=out/logs\n"
        "CALCULATOR_HISTORY_DIR=out/history\n"
        "CALCULATOR_MAX_HISTORY_SIZE=5\n"
        "CALCULATOR_PRECISION=2\n"
        "CALCULATOR_MAX_INPUT_VALUE=500\n"
        "CALCULATOR_DEFAULT_ENCODING=latin-1\n"
    )
    config = CalculatorConfig.from_env(env_file=str(env_file))
    assert config.log_file == Path("out/logs/calculator.log")
    assert config.history_file == Path("out/history/history.csv")
    assert (config.max_history_size, config.precision, config.max_input_value) == (5, 2, 500.0)
    assert config.encoding == "latin-1"


def test_explicit_file_paths_override_directories(monkeypatch):
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "custom.log")
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "saved.csv")
    config = CalculatorConfig.from_env(env_file="missing.env")
    assert (config.log_file, config.history_file) == (Path("custom.log"), Path("saved.csv"))


@pytest.mark.parametrize("value, expected", [("true", True), ("YES", True), ("0", False), ("no", False)])
def test_auto_save_values(monkeypatch, value, expected):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    assert CalculatorConfig.from_env(env_file="missing.env").auto_save is expected


@pytest.mark.parametrize("name, value", [
    ("CALCULATOR_MAX_HISTORY_SIZE", "ten"),
    ("CALCULATOR_MAX_HISTORY_SIZE", "0"),
    ("CALCULATOR_PRECISION", "-1"),
    ("CALCULATOR_MAX_INPUT_VALUE", "-5"),
    ("CALCULATOR_DEFAULT_ENCODING", "not-an-encoding"),
    ("CALCULATOR_AUTO_SAVE", "maybe"),
])
def test_invalid_settings(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError):
        CalculatorConfig.from_env(env_file="missing.env")
