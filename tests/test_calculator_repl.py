import pytest

from app.calculator_repl import CalculatorREPL


def run(calculator, monkeypatch, capsys, inputs):
    answers = iter(inputs + ["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    CalculatorREPL(calculator).run()
    return capsys.readouterr().out


@pytest.mark.parametrize("inputs, expected", [
    (["help"], "int_divide  a / b with the fraction discarded"),
    (["help"], "undo        undo the last change"),
    (["history"], "History is empty."),
    (["add", "2", "3"], "Result: 5.0"),
    (["abs_diff", "2", "9"], "Result: 7.0"),
    (["add", "2", "3", "history"], "1. add(2.0, 3.0) = 5.0"),
    (["divide", "1", "0"], "Error: Cannot divide by zero"),
    (["root", "x", "2"], "Error: 'x' is not a number"),
    (["banana"], "Unknown command 'banana'"),
    (["clear"], "History cleared."),
    (["undo"], "Nothing to undo."),
    (["redo"], "Nothing to redo."),
    (["add", "1", "1", "undo"], "Undone."),
    (["add", "1", "1", "undo", "redo"], "Redone."),
    (["load"], "No saved history found."),
    ([], "Goodbye."),
])
def test_commands(calculator, monkeypatch, capsys, inputs, expected):
    assert expected in run(calculator, monkeypatch, capsys, inputs)


def test_output_is_color_coded(calculator, monkeypatch, capsys):
    out = run(calculator, monkeypatch, capsys, ["add", "1", "1", "divide", "1", "0"])
    assert "\x1b[32mResult: 2.0" in out
    assert "\x1b[31mError: Cannot divide by zero" in out


def test_save_then_load(calculator, monkeypatch, capsys):
    out = run(calculator, monkeypatch, capsys, ["add", "1", "1", "save", "load"])
    assert "Saved to" in out
    assert "Loaded 1 calculations." in out


def test_saved_history_loads_on_start(calculator, monkeypatch, capsys):
    calculator.calculate("add", "1", "1")
    calculator.save()
    out = run(calculator, monkeypatch, capsys, [])
    assert "Loaded 1 calculations." in out


def test_malformed_history_does_not_stop_the_repl(calculator, monkeypatch, capsys):
    calculator.config.history_file.parent.mkdir(parents=True)
    calculator.config.history_file.write_text("nonsense\n")
    out = run(calculator, monkeypatch, capsys, ["add", "1", "1"])
    assert "Error: History file" in out
    assert "Result: 2.0" in out


def test_auto_save_writes_after_calculation(calculator, monkeypatch, capsys):
    calculator.config.auto_save = True
    run(calculator, monkeypatch, capsys, ["add", "1", "1"])
    assert calculator.load() is True


def test_errors_and_unknown_commands_are_logged(calculator, monkeypatch, capsys, caplog):
    with caplog.at_level("WARNING"):
        run(calculator, monkeypatch, capsys, ["divide", "1", "0", "banana"])
    assert "ERROR" in caplog.text and "OperationError: Cannot divide by zero" in caplog.text
    assert "Unknown command: banana" in caplog.text
