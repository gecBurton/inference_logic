import pytest

from inference_logic import Rule, Variable
from inference_logic.data_structures import construct, new_frame

A, B = Variable.factory("A", "B")
A_1 = Variable("A", 1)
B_1 = Variable("B", 1)


@pytest.mark.parametrize(
    "initial, final",
    [
        (True, True),
        (A, Variable("A", 1)),
        ((A, True), (A_1, True)),
        (dict(a=A), dict(a=A_1)),
    ],
)
def test_new_frame_function(initial, final):
    assert new_frame(construct(initial), 1) == construct(final)


@pytest.mark.parametrize(
    "initial, final", [(Rule(dict(a=A), dict(b=B)), Rule(dict(a=A_1), dict(b=B_1)))],
)
def test_new_frame_method(initial, final):
    assert construct(initial).new_frame(1) == construct(final)
