import pytest

from inference_logic import Variable


def test__init__error():
    with pytest.raises(ValueError) as error:
        Variable(1)
    assert str(error.value) == "name must be a string"


def test_factory():
    assert Variable.factory("A", "B") == [Variable("A"), Variable("B")]


@pytest.mark.parametrize("name, frame, message", [("A", None, "A"), ("A", 2, "A:2")])
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
