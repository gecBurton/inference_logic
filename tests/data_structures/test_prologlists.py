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
    with pytest.raises(UnificationError) as error:
        PrologListNull() == 0
    assert str(error.value) == "0 must be a PrologListNull"

    with pytest.raises(UnificationError) as error:
        PrologList(1, 2) == 0
    assert str(error.value) == "0 must be a PrologList"


def test_list__repr__():
    assert repr(construct([1, [2, 3], 4])) == "[1, [2, 3], 4]"


def test_list__len__():
    assert len(construct([1, [2, 3], 4])) == 3


def test_list__add__():
    a = construct([1, 2])
    b = construct([3, 4])
    assert a + b == construct([1, 2, 3, 4])


def test_list__add__fail():
    a = construct([1, 2])
    with pytest.raises(UnificationError) as error:
        a + 3
    assert str(error.value) == "3 must be a PrologList"


def test_list_in():
    a = construct([1, 2])
    assert 1 in a
    assert 3 not in a


def test_list__iter__():
    a = construct([1, 2])
    assert list(a) == [1, 2]


def test_list_null_in():
    a = construct([])
    assert 1 not in a
