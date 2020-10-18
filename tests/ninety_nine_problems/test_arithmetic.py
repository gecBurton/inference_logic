from inference_logic.algorithms import search
from inference_logic.data_structures import Assert, Assign, Rule, Variable


def test_31():
    """
    P31 (**) Determine whether a given integer number is prime.

    is_prime(P) :- P is a prime number
       (integer) (+)

    is_prime(2).
    is_prime(3).
    is_prime(P) :- integer(P), P > 3, P mod 2 =\\= 0, \\+ has_factor(P,3).

    has_factor(N,L) :- N has an odd factor F >= L.
       (integer, integer) (+,+)

    has_factor(N,L) :- N mod L =:= 0.
    has_factor(N,L) :- L * L < N, L2 is L + 2, has_factor(N,L2).
    """

    N, L, L2, Q, P = Variable.factory("N", "L", "L2", "Q", "P")

    db = [
        dict(is_prime=2),
        dict(is_prime=3),
        Rule(
            dict(is_prime=P),
            Assert(lambda P: isinstance(P, int)),
            Assert(lambda P: P > 3),
            Assert(lambda P: P % 2 != 0),
            dict(has_factor=P, x=3),
        ),
        Rule(dict(has_factor=N, x=L), Assert(lambda N, L: N % L != 0)),
        Rule(
            dict(has_factor=N, x=L),
            Assert(lambda L, N: L * L < N),
            Assign(L2, lambda L: L + 2),
            dict(has_factor=N, x=L2),
        ),
    ]

    assert list(search(db, dict(is_prime=3))) == [{}]
    assert list(search(db, dict(is_prime=3.5))) == []
    assert list(search(db, dict(is_prime=4))) == []
    assert list(search(db, dict(is_prime=5))) == [{}]
    assert list(search(db, dict(is_prime=6))) == []
    assert list(search(db, dict(is_prime=7))) == [{}]


def test_32():
    """
    P32 (**) Determine the greatest common divisor of two positive integers.

    gcd(X,Y,G) :- G is the greatest common divisor of X and Y
       (integer, integer, integer) (+,+,?)


    gcd(X,0,X) :- X > 0.
    gcd(X,Y,G) :- Y > 0, Z is X mod Y, gcd(Y,Z,G).


    Declare gcd as an arithmetic function; so you can use it
    like this:  ?- G is gcd(36,63).

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


def test_33():
    """
    P33 (*) Determine whether two positive integer numbers are coprime.
        Two numbers are coprime if their greatest common divisor equals 1.

    coprime(X,Y) :- X and Y are coprime.
       (integer, integer) (+,+)

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
