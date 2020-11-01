import pytest

from inference_logic import Variable
from inference_logic.data_structures import UnificationError, construct
from inference_logic.equality import Equality

A, B, C = Variable.factory("A", "B", "C")


@pytest.mark.parametrize(
    "left, right, initial, final",
    [
        (A, False, Equality(), Equality(fixed={False: {A}})),
        (True, B, Equality(), Equality(fixed={True: {B}})),
        (1, 1, Equality(), Equality()),
        (A, B, Equality(), Equality(free=[{A, B}])),
        ((A, B), (1, 2), Equality(), Equality(fixed={1: {A}, 2: {B}})),
        (dict(a=A, b=2), dict(a=1, b=B), Equality(), Equality(fixed={1: {A}, 2: {B}}),),
        (A, C, Equality(free=[{A, B}]), Equality(free=[{A, B, C}])),
        (A, 1, Equality(free=[{A, B}]), Equality(fixed={1: {A, B}})),
        (
            (A, *B),
            (True, False),
            Equality(),
            Equality(fixed={True: {A}, construct([False]): {B}}),
        ),
        (
            (A, *B),
            (1, 2, 3),
            Equality(),
            Equality(fixed={1: {A}, construct([2, 3]): {B}}),
        ),
        (*B, (2, 3), Equality(), Equality(fixed={construct([2, 3]): {B}})),
    ],
)
def test_unify_pass(left, right, initial, final):
    left, right = construct(left), construct(right)
    assert initial.unify(left, right) == final


@pytest.mark.parametrize(
    "left, right, initial, message",
    [
        (True, False, Equality(), "values dont match: True != False"),
        ((A, B), (1, 2, 3), Equality(), "list lengths must be the same"),
        (
            dict(a=1, b=2),
            dict(a=1, c=3),
            Equality(),
            "keys must match: ('a', 'b') != ('a', 'c')",
        ),
        (
            B,
            False,
            Equality(fixed={True: {A, B}}),
            "B cannot equal False because False != True",
        ),
    ],
)
def test_unify_fail(left, right, initial, message):
    left, right = construct(left), construct(right)
    with pytest.raises(UnificationError) as error:
        initial.unify(left, right)
    assert str(error.value) == message
