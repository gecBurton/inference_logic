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
