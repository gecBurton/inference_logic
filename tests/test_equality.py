import pytest

from inference_logic import Variable
from inference_logic.data_structures import ImmutableDict, UnificationError, construct
from inference_logic.equality import Equality

A, B, C, D = Variable.factory("A", "B", "C", "D")


def test__repr__():
    equity = Equality(free=[{A}], fixed={True: {C}})
    assert repr(equity) == "Equality({A}, True={C})"


@pytest.mark.parametrize(
    "method, args, message",
    [
        ("__eq__", (1,), "1 must be an Equality"),
        ("get_free", (1,), "1 must be a Variable"),
        ("get_fixed", (1,), "1 must be a Variable"),
        ("_add_constant", (1, 2), "1 must be a Variable"),
        ("_add_constant", (A, B), "B may not be a Variable"),
        ("_add_constant", (A, {1, 2}), "{1, 2} must be hashable"),
        ("_add_variable", (1, 2), "1 must be a Variable"),
        ("_add_variable", (A, 2), "2 must be a Variable"),
    ],
)
def test_type_error(method, args, message):

    equity = Equality()
    with pytest.raises(TypeError) as error:
        getattr(equity, method)(*args)
    assert str(error.value) == message


def test__hash__():
    # this is about all we can do for a hash test
    # without just reproducing the logic her
    equity = Equality(free=[{A}], fixed={True: {C}})
    assert isinstance(hash(equity), int)


def test__eq__():
    equity = Equality(free=[{A}], fixed={True: {C}})
    assert equity == Equality(free=[{A}], fixed={True: {C}})
    assert equity != Equality(free=[{A}])


@pytest.mark.parametrize("variable, result", [(A, {A, B}), (B, {A, B}), (C, set())])
def test_get_free(variable, result):
    equity = Equality(free=[{A, B}], fixed={True: {C}})
    assert equity.get_free(variable) == result


@pytest.mark.parametrize("variable, result", [(A, True), (B, True), (C, False)])
def test_get_fixed(variable, result):
    equity = Equality(fixed={True: {A, B}, False: {C}})
    assert equity.get_fixed(variable) == result


def test_get_fixed_fail():
    equity = Equality()
    with pytest.raises(KeyError):
        equity.get_fixed(A)


@pytest.mark.parametrize(
    "left, right, initial, final",
    [
        (True, True, Equality(), Equality()),
        (A, True, Equality(), Equality(fixed={True: {A}})),
        (A, True, Equality(fixed={True: {A}}), Equality(fixed={True: {A}})),
        (True, A, Equality(), Equality(fixed={True: {A}})),
        (A, B, Equality(), Equality(free=[{A, B}])),
        (A, B, Equality(fixed={True: {B}}), Equality(fixed={True: {A, B}})),
        (A, B, Equality(free=[{B, C}]), Equality(free=[{A, B, C}])),
        (A, True, Equality(free=[{A, B}]), Equality(fixed={True: {A, B}})),
        (A, B, Equality(free=[{A, C}, {B, D}]), Equality(free=[{A, B, C, D}])),
        (
            A,
            B,
            Equality(free=[{B, C}], fixed={True: {A}}),
            Equality(fixed={True: {A, B, C}}),
        ),
        (A, B, Equality(fixed={True: {A}}), Equality(fixed={True: {A, B}})),
        (A, B, Equality(free=[{A, C}]), Equality(free=[{A, B, C}])),
        (
            A,
            B,
            Equality(free=[{A, C}], fixed={True: {B}}),
            Equality(fixed={True: {A, B, C}}),
        ),
    ],
)
def test_add(left, right, initial, final):
    assert initial.add(left, right) == final


@pytest.mark.parametrize(
    "left, right, initial, message",
    [
        (
            A,
            B,
            Equality(fixed={True: {A}, False: {B}}),
            "A cannot equal B because True != False",
        ),
        (A, B, Equality(fixed={1: {A}, 2: {B}}), "A cannot equal B because 1 != 2"),
        (
            A,
            1,
            Equality(free=[{A, B}], fixed={2: {B}}),
            "A cannot equal 1 because 1 != 2",
        ),
        (True, False, Equality(), "values dont match: True != False"),
    ],
)
def test_add_fail(left, right, initial, message):
    with pytest.raises(UnificationError) as error:
        initial.add(left, right)
    assert str(error.value) == message


@pytest.mark.parametrize(
    "equality, to_solve_for, initial, final",
    [
        (
            Equality(free=[{C, D}], fixed={1: {A}, 2: {B}}),
            None,
            ImmutableDict(a=A, b=B, c=C),
            {ImmutableDict(a=1, b=2, c=C)},
        ),
        (
            Equality(free=[{C, D}], fixed={1: {A, B}}),
            None,
            ImmutableDict(a=A, b=(B, False), c=ImmutableDict(a=B)),
            {ImmutableDict(a=1, b=(1, False), c=ImmutableDict(a=1))},
        ),
        (
            Equality(free=[{C, D}], fixed={1: {A, B}}),
            {D},
            ImmutableDict(a=A, b=(B, C), c=ImmutableDict(a=B)),
            {ImmutableDict(a=1, b=(1, D), c=ImmutableDict(a=1))},
        ),
        (
            Equality(free=[{A, B, C}]),
            {B, C},
            ImmutableDict(a=A),
            {ImmutableDict(a=B), ImmutableDict(a=C)},
        ),
    ],
)
def test_inject(equality, to_solve_for, initial, final):
    assert equality.inject(initial, to_solve_for=to_solve_for) == final


@pytest.mark.parametrize(
    "variable, expected",
    [
        (A, 1),
        ([A, True], (1, True)),
        ({"a": [A, {"b": False}]}, {"a": [1, {"b": False}]}),
    ],
)
def test_get_deep(variable, expected):
    equality = Equality(fixed={1: {A}}, free=[{B, C}])
    assert equality.get_deep(construct(variable)) == construct(expected)


def test_recursions_error():
    a = construct([A, B])
    equality = Equality(fixed={a: {B}, 1: {A}})
    with pytest.raises(RecursionError) as error:
        equality.get_deep(a)
    assert str(error.value) == "maximum recursion depth exceeded in comparison"
