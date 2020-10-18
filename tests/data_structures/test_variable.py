import pytest

from inference_logic import Variable


@pytest.mark.parametrize(
    "name, message",
    [("a", "name must begin with a uppercase letter"), (1, "name must be a string")],
)
def test__init__error(name, message):
    with pytest.raises(ValueError) as error:
        Variable(name)
    assert str(error.value) == message


def test_factory():
    assert Variable.factory("A", "B") == [Variable("A"), Variable("B")]


@pytest.mark.parametrize("name, frame, message", [("A", None, "A"), ("A", 2, "A_2")])
def test__repr__(name, frame, message):
    assert repr(Variable(name, frame)) == message


def test__eq__():
    assert Variable("A") == Variable("A")
    assert Variable("A") != Variable("B")

    with pytest.raises(TypeError) as error:
        Variable("A") == "A"
    assert str(error.value) == "A must be a Variable"


def test_new_frame():
    assert Variable("A", 3).new_frame(4) == Variable("A", 4)
