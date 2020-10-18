import pytest

from inference_logic import Rule


@pytest.mark.parametrize(
    "head, body, representation",
    [
        (dict(a=1), tuple(), "{'a': 1}."),
        (dict(a=1), (dict(b=2),), "{'a': 1} ¬ {'b': 2}."),
        (dict(a=1), (dict(b=2), dict(c=3)), "{'a': 1} ¬ {'b': 2} ∧ {'c': 3}.",),
    ],
)
def test__init__repr(head, body, representation):
    assert repr(Rule(head, *body)) == representation


def test__eq__():
    im1 = dict(a=1)
    im2 = dict(b=2)
    assert Rule(im1, im2) == Rule(im1, im2)
    assert Rule(im1, im2) != Rule(im2, im1)


def test__eq__fail():
    with pytest.raises(TypeError) as error:
        Rule(dict()) == 1
    assert str(error.value) == "1 must be a Rule"
