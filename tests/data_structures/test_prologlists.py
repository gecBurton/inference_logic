import pytest

from inference_logic.data_structures import (
    PrologList,
    PrologListNull,
    UnificationError,
    construct,
)


def test__repr__():

    assert repr(construct([1, [2, 3], 4])) == "[1, [2, 3], 4]"


def test__eq__fail():
    with pytest.raises(TypeError) as error:
        PrologListNull() == 0
    assert str(error.value) == "0 must be a PrologListNull"

    with pytest.raises(UnificationError) as error:
        PrologList(1, 2) == 0
    assert str(error.value) == "0 must be a PrologList"


def test_list__repr__():
    assert repr(construct([1, [2, 3], 4])) == "[1, [2, 3], 4]"
