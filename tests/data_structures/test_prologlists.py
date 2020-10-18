import pytest

from inference_logic.data_structures import PrologListNull, construct


def test_null__repr__():

    assert repr(PrologListNull()) == ".()"


def test__eq__fail():
    with pytest.raises(TypeError) as error:
        PrologListNull() == 0
    assert str(error.value) == "0 must be a PrologListNull"


def test_list__repr__():
    assert repr(construct([1, [2, 3], 4])) == ".(1, .(.(2, .(3, .())), .(4, .())))"
