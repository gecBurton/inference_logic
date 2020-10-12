import pytest

from json_inference_logic import ImmutableDict, Variable
from json_inference_logic.data_structures import PrologList


def test__init__():
    im = ImmutableDict(a=1, b=["2", {"c": None}])
    assert im["a"] == 1
    assert isinstance(im["b"], PrologList)
    assert im["b"][0] == "2"
    assert isinstance(im["b"][1], ImmutableDict)
    assert im["b"][1]["c"] is None


@pytest.mark.parametrize(
    "args, kwargs, message",
    [
        (tuple(), dict(a={1, 2}), "{1, 2} is not json serializable"),
        (({1: 2},), {}, "1 must be a string"),
        (({1: 2}, {1: 2}), {}, "expected at most 1 arguments, got 2"),
    ],
)
def test__init__error(args, kwargs, message):
    with pytest.raises(TypeError) as error:
        ImmutableDict(*args, **kwargs)
    assert str(error.value) == message


def test__init__warn():
    with pytest.warns(DeprecationWarning) as warning:
        ImmutableDict(dict={})
    assert str(warning[0].message) == "Passing 'dict' as keyword argument is deprecated"


def test__hash__():
    assert hash((("a", 1),)) == hash(ImmutableDict(a=1))


def test__eq__():
    assert ImmutableDict(a=1) == ImmutableDict(a=1)
    assert ImmutableDict(a=1) != ImmutableDict(b=1)
    with pytest.raises(TypeError) as error:
        ImmutableDict(a=1) == dict(b=1)
    assert str(error.value) == "{'b': 1} must be an ImmutableDict"


def test_immutable():
    im = ImmutableDict(a=1)
    with pytest.raises(TypeError) as error:
        im["a"] = 2

    assert str(error.value) == "object is immutable"


def test_get_variables():
    A, B, C = Variable.factory("A", "B", "C")
    im = ImmutableDict(a=A, b=(1, B), c=ImmutableDict(d=(C, False)))
    assert im.get_variables() == {A, B, C}
