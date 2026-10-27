"""The read-eval-print loop, with each command as a Command object."""

from abc import ABC, abstractmethod

from colorama import Fore, Style

from app.calculator import Calculator
from app.exceptions import CalculatorError
from app.history import AutoSaveObserver, LoggingObserver
from app.logger import Logger
from app.operations import OperationFactory

logger = Logger.get(__name__)


def success(text):
    print(Fore.GREEN + text + Style.RESET_ALL)


def info(text):
    print(Fore.CYAN + text + Style.RESET_ALL)


def error(text):
    print(Fore.RED + text + Style.RESET_ALL)


class Command(ABC):
    """Command pattern: each REPL command is an object with one execute method."""

    description = ""

    def __init__(self, calculator):
        self.calculator = calculator

    @abstractmethod
    def execute(self):
        raise NotImplementedError  # pragma: no cover


class CalculateCommand(Command):
    def __init__(self, calculator, operation):
        super().__init__(calculator)
        self.operation = operation

    def execute(self):
        a = input("First number: ")
        b = input("Second number: ")
        success(f"Result: {self.calculator.calculate(self.operation, a, b)}")


class HistoryCommand(Command):
    description = "show the calculations so far"

    def execute(self):
        entries = self.calculator.history.entries()
        if not entries:
            info("History is empty.")
        for number, calculation in enumerate(entries, start=1):
            print(f"{number}. {calculation}")


class ClearCommand(Command):
    description = "empty the history (can be undone)"

    def execute(self):
        self.calculator.clear()
        success("History cleared.")


class UndoCommand(Command):
    description = "undo the last change"

    def execute(self):
        if self.calculator.undo():
            success("Undone.")
        else:
            info("Nothing to undo.")


class RedoCommand(Command):
    description = "redo the last undone change"

    def execute(self):
        if self.calculator.redo():
            success("Redone.")
        else:
            info("Nothing to redo.")


class SaveCommand(Command):
    description = "save the history to CSV"

    def execute(self):
        self.calculator.save()
        success(f"Saved to {self.calculator.config.history_file}.")


class LoadCommand(Command):
    description = "load the history from CSV"

    def execute(self):
        if self.calculator.load():
            success(f"Loaded {len(self.calculator.history)} calculations.")
        else:
            info("No saved history found.")


class HelpCommand(Command):
    description = "list operations and commands"

    def __init__(self, calculator, commands):
        super().__init__(calculator)
        self.commands = commands

    def execute(self):
        info("Operations:")
        for name, description in OperationFactory.descriptions():
            print(f"  {name:<11} {description}")
        info("Commands:")
        for name, command in self.commands.items():
            print(f"  {name:<11} {command.description}")
        print(f"  {'exit':<11} quit the calculator")


class CalculatorREPL:
    """Reads a command, runs it, prints the outcome, and repeats until exit."""

    def __init__(self, calculator=None):
        self.calculator = calculator or Calculator()
        self.calculator.attach(LoggingObserver())
        self.calculator.attach(AutoSaveObserver(self.calculator))
        self.commands = {
            "history": HistoryCommand(self.calculator),
            "clear": ClearCommand(self.calculator),
            "undo": UndoCommand(self.calculator),
            "redo": RedoCommand(self.calculator),
            "save": SaveCommand(self.calculator),
            "load": LoadCommand(self.calculator),
        }
        self.commands["help"] = HelpCommand(self.calculator, self.commands)

    def run(self):
        self.execute(LoadCommand(self.calculator))
        info("Calculator ready. Type 'help' for commands or 'exit' to quit.")
        while True:
            name = input("calc> ").strip().lower()
            if name == "exit":
                info("Goodbye.")
                break
            command = self.find(name)
            if command is None:
                logger.warning("Unknown command: %s", name)
                error(f"Unknown command '{name}'. Type 'help' for options.")
            else:
                self.execute(command)

    def find(self, name):
        if name in self.commands:
            return self.commands[name]
        if name in OperationFactory.names():
            return CalculateCommand(self.calculator, name)
        return None

    def execute(self, command):
        try:
            command.execute()
        except CalculatorError as problem:
            logger.error("%s: %s", type(problem).__name__, problem)
            error(f"Error: {problem}")
