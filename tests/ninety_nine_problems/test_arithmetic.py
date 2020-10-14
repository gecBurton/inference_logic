from json_inference_logic.algorithms import search
from json_inference_logic.data_structures import Assert, Assign, Rule, Variable


def test_determine_the_greatest_common_divisor_of_two_positive_integer_numbers_32():
    """
    % P32 (**) Determine the greatest common divisor of two positive integers.

    % gcd(X,Y,G) :- G is the greatest common divisor of X and Y
    %    (integer, integer, integer) (+,+,?)


    gcd(X,0,X) :- X > 0.
    gcd(X,Y,G) :- Y > 0, Z is X mod Y, gcd(Y,Z,G).


    % Declare gcd as an arithmetic function; so you can use it
    % like this:  ?- G is gcd(36,63).

    :- arithmetic_function(gcd/2).
    """
    X, Y, Z, G, Q = Variable.factory("X", "Y", "Z", "G", "Q")
    db = [
        Rule(dict(a=X, b=0, gcd=X), Assert(lambda X: X > 0)),
        Rule(
            dict(a=X, b=Y, gcd=G),
            Assert(lambda Y: Y > 0),
            Assign(Z, lambda X, Y: X % Y),
            dict(a=Y, b=Z, gcd=G),
        ),
    ]
    assert list(search(db, dict(a=36, b=63, gcd=Q))) == [{Q: 9}]


def test_determine_whether_two_positive_integer_numbers_are_coprime_33():
    """
    % P33 (*) Determine whether two positive integer numbers are coprime.
    %     Two numbers are coprime if their greatest common divisor equals 1.

    % coprime(X,Y) :- X and Y are coprime.
    %    (integer, integer) (+,+)

    :- ensure_loaded(p32).

    coprime(X,Y) :- gcd(X,Y,1).
    """
    X, Y, Z, G, Q = Variable.factory("X", "Y", "Z", "G", "Q")
    db = [
        Rule(dict(a=X, b=0, gcd=X), Assert(lambda X: X > 0)),
        Rule(
            dict(a=X, b=Y, gcd=G),
            Assert(lambda Y: Y > 0),
            Assign(Z, lambda X, Y: X % Y),
            dict(a=Y, b=Z, gcd=G),
        ),
        Rule(dict(a=X, b=Y, coprime=True), dict(a=X, b=Y, gcd=1)),
    ]
    query = dict(a=15, b=4, coprime=Q)
    assert list(search(db, query)) == [{Q: True}]
