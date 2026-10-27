# Enhanced Calculator

A command-line calculator that runs as a REPL. It has ten operations, keeps
its history in a pandas DataFrame saved as CSV, supports undo and redo, logs
every calculation and error to a file, and reads its settings from a .env
file. Output is color-coded: results in green, errors in red, information in
cyan.

## Installation

    git clone https://github.com/Chima765432/is601-midterm-calculator.git
    cd is601-midterm-calculator
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Configuration

Settings live in a .env file in the project folder. The repository includes
one with these values:

    CALCULATOR_LOG_DIR=logs
    CALCULATOR_HISTORY_DIR=history
    CALCULATOR_MAX_HISTORY_SIZE=100
    CALCULATOR_AUTO_SAVE=true
    CALCULATOR_PRECISION=4
    CALCULATOR_MAX_INPUT_VALUE=1000000000000
    CALCULATOR_DEFAULT_ENCODING=utf-8

- CALCULATOR_LOG_DIR: folder for the log file
- CALCULATOR_HISTORY_DIR: folder for the history CSV
- CALCULATOR_MAX_HISTORY_SIZE: how many calculations to keep
- CALCULATOR_AUTO_SAVE: save the history after every calculation (true or false)
- CALCULATOR_PRECISION: decimal places results are rounded to
- CALCULATOR_MAX_INPUT_VALUE: largest number accepted as input
- CALCULATOR_DEFAULT_ENCODING: encoding for the log and CSV files

Two optional settings point at exact files instead of the folders:
CALCULATOR_LOG_FILE (default logs/calculator.log) and CALCULATOR_HISTORY_FILE
(default history/history.csv). Any setting left out falls back to its
default, and an invalid value, such as a negative precision or an unknown
encoding, stops the program with a message saying which setting is wrong.

## Logging

Logs go to the file set by CALCULATOR_LOG_DIR or CALCULATOR_LOG_FILE. Each
calculation is logged at INFO with its operation, operands, and result.
Saving and loading are logged at INFO, a missing history file and unknown
commands at WARNING, and failed calculations or unreadable files at ERROR.

## Usage

    python main.py

Type an operation, then enter the two numbers when asked:

| Operation  | Result                           |
|------------|----------------------------------|
| add        | a + b                            |
| subtract   | a - b                            |
| multiply   | a * b                            |
| divide     | a / b                            |
| power      | a raised to the power b          |
| root       | the b-th root of a               |
| modulus    | remainder of a / b               |
| int_divide | a / b with the fraction discarded |
| percent    | a as a percentage of b           |
| abs_diff   | absolute difference of a and b   |

Other commands:

- help: list operations and commands
- history: show the calculations so far
- clear: empty the history (can be undone)
- undo / redo: step back or forward through changes
- save / load: write the history to CSV or read it back
- exit: quit

Saved history loads automatically on start. Invalid input, division by zero,
numbers over the maximum, and unreadable history files print a red error
message and the calculator keeps running.

## Design

- Factory and Strategy (operations.py): each operation is a class with a
  compute method, and OperationFactory builds the one matching the name typed.
- Decorator (operations.py): each operation registers itself with
  @OperationFactory.register, and the help menu is built from that registry,
  so adding an operation adds it to help automatically.
- Observer (history.py): LoggingObserver logs each calculation and
  AutoSaveObserver saves the history to CSV after each calculation.
- Memento (calculator_memento.py): a copy of the history is saved before every
  change, which is what undo and redo restore.
- Facade (calculator.py): the Calculator class is the single interface the
  REPL uses.
- Command (calculator_repl.py): each REPL command is an object with an
  execute method.

## Testing

    pytest

This runs every test with coverage and fails if coverage drops below 90
percent. For an HTML coverage report, run pytest --cov=app --cov-report=html
and open htmlcov/index.html.

## CI/CD

The GitHub Actions workflow in .github/workflows/python-app.yml runs on every
push and pull request to main. It installs the dependencies, runs the full
test suite with coverage, and fails the build if coverage is below 90
percent, so a change that breaks a test or leaves new code untested is caught
before it is merged.
