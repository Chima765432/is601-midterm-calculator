import pandas as pd
import pytest

from app.calculator_memento import CalculatorMemento


@pytest.mark.parametrize("rows", [[], [{"result": 1}], [{"result": 1}, {"result": 2}]])
def test_restore_returns_an_independent_copy(rows):
    frame = pd.DataFrame(rows, columns=["result"])
    memento = CalculatorMemento(frame)
    frame.loc[len(frame)] = [99]
    restored = memento.restore()
    assert len(restored) == len(rows)
    restored.loc[len(restored)] = [100]
    assert len(memento.restore()) == len(rows)
