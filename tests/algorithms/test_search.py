from inference_logic import Rule, Variable
from inference_logic.algorithms import search

X, Y, Z, C, P = Variable.factory("X", "Y", "Z", "C", "P")

db = [
    dict(parent="G", child="A"),
    dict(parent="A", child="O"),
    Rule(dict(ancestor=X, descendant=Z), dict(parent=X, child=Z)),
    Rule(
        dict(ancestor=X, descendant=Z),
        dict(parent=X, child=Y),
        dict(ancestor=Y, descendant=Z),
    ),
]

query = dict(ancestor=P, descendant=C)


def test_search():
    assert list(search(db, query)) == [
        {P: "G", C: "O"},
        {P: "G", C: "A"},
        {P: "A", C: "O"},
    ]
