import pytest

from json_inference_logic import ImmutableDict, Rule, Variable, new_frame

A, B = Variable.factory("A", "B")
A_1 = Variable("A", 1)
B_1 = Variable("B", 1)


@pytest.mark.parametrize(
    "initial, final",
    [
        (True, True),
        (A, Variable("A", 1)),
        ((A, True), (A_1, True)),
        (ImmutableDict(a=A), ImmutableDict(a=A_1)),
        (
            Rule(ImmutableDict(a=A), ImmutableDict(b=B)),
            Rule(ImmutableDict(a=A_1), ImmutableDict(b=B_1)),
        ),
    ],
)
def test_new_frame(initial, final):
    assert new_frame(initial, 1) == final
