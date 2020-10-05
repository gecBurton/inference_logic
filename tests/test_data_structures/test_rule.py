import pytest

from json_inference_logic import ImmutableDict, Rule


@pytest.mark.parametrize(
    "head, body, representation",
    [
        (ImmutableDict(a=1), tuple(), "{'a': 1}."),
        (ImmutableDict(a=1), (ImmutableDict(b=2),), "{'a': 1} ¬ {'b': 2}."),
        (
            ImmutableDict(a=1),
            (ImmutableDict(b=2), ImmutableDict(c=3)),
            "{'a': 1} ¬ {'b': 2} ∧ {'c': 3}.",
        ),
    ],
)
def test__init__repr(head, body, representation):
    assert repr(Rule(head, *body)) == representation


@pytest.mark.parametrize(
    "head, body, message",
    [
        (1, (ImmutableDict(a=1),), "head must be an ImmutableDict"),
        (ImmutableDict(a=1), (2,), "all args in body must be ImmutableDicts"),
    ],
)
def test__init__fail(head, body, message):
    with pytest.raises(TypeError) as error:
        repr(Rule(head, *body))
    assert str(error.value) == message


def test__eq__():
    im1 = ImmutableDict(a=1)
    im2 = ImmutableDict(b=2)
    assert Rule(im1, im2) == Rule(im1, im2)
    assert Rule(im1, im2) != Rule(im2, im1)


def test__eq__fail():
    with pytest.raises(TypeError) as error:
        Rule(ImmutableDict()) == 1
    assert str(error.value) == "1 must be a Rule"
