"""Starts the calculator."""

from colorama import just_fix_windows_console

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import CalculatorREPL
from app.logger import Logger

if __name__ == "__main__":
    just_fix_windows_console()
    config = CalculatorConfig.from_env()
    Logger.setup(config)
    CalculatorREPL(Calculator(config)).run()
