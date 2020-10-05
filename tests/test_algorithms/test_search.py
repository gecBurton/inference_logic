from json_inference_logic import ImmutableDict, Rule, Variable
from json_inference_logic.algorithms import search
from json_inference_logic.equality import Equality

X, Y, Z, C, P = Variable.factory("X", "Y", "Z", "C", "P")

db = [
    ImmutableDict(parent="Gulia", child="Albert"),
    ImmutableDict(parent="Albert", child="Aurelie"),
    Rule(ImmutableDict(ancestor=X, descendant=Z), ImmutableDict(parent=X, child=Z)),
    Rule(
        ImmutableDict(ancestor=X, descendant=Z),
        ImmutableDict(parent=X, child=Y),
        ImmutableDict(ancestor=Y, descendant=Z),
    ),
]

query = ImmutableDict(ancestor=P, descendant=C)


def test_search():
    assert set(search(db, query)) == {
        Equality(fixed={"Gulia": {P}, "Aurelie": {C}}),
        Equality(fixed={"Gulia": {P}, "Albert": {C}}),
        Equality(fixed={"Albert": {P}, "Aurelie": {C}}),
    }
