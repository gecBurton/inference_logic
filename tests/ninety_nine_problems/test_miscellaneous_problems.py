import pytest

from inference_logic import Rule, Variable, search
from inference_logic.data_structures import Assert, Assign


@pytest.mark.xfail
def test_90():
    r"""
    P90 (**) Eight queens problem

    This is a classical problem in computer science. The objective is to
    place eight queens on a chessboard so that no two queens are attacking
    each other; i.e., no two queens are in the same row, the same column,
    or on the same diagonal. We generalize this original problem by
    allowing for an arbitrary dimension N of the chessboard.

    We represent the positions of the queens as a list of numbers 1..N.
    Example: [4,2,7,3,6,8,5,1] means that the queen in the first column
    is in row 4, the queen in the second column is in row 2, etc.
    By using the permutations of the numbers 1..N we guarantee that
    no two queens are in the same row. The only test that remains
    to be made is the diagonal test. A queen placed at column X and
    row Y occupies two diagonals: one of them, with number C = X-Y, goes
    from bottom-left to top-right, the other one, numbered D = X+Y, goes
    from top-left to bottom-right. In the test predicate we keep track
    of the already occupied diagonals in Cs and Ds.

    % The first version is a simple generate-and-test solution.

    % queens_1(N,Qs) :- Qs is a solution of the N-queens problem

    queens_1(N,Qs) :- range(1,N,Rs), permu(Rs,Qs), test(Qs).

    % range(A,B,L) :- L is the list of numbers A..B

    range(A,A,[A]).
    range(A,B,[A|L]) :- A < B, A1 is A+1, range(A1,B,L).

    % permu(Xs,Zs) :- the list Zs is a permutation of the list Xs

    permu([],[]).
    permu(Qs,[Y|Ys]) :- del(Y,Qs,Rs), permu(Rs,Ys).

    del(X,[X|Xs],Xs).
    del(X,[Y|Ys],[Y|Zs]) :- del(X,Ys,Zs).

    % test(Qs) :- the list Qs represents a non-attacking queens solution

    test(Qs) :- test(Qs,1,[],[]).

    % test(Qs,X,Cs,Ds) :- the queens in Qs, representing columns X to N,
    % are not in conflict with the diagonals Cs and Ds

    test([],_,_,_).
    test([Y|Ys],X,Cs,Ds) :-
        C is X-Y, \+ memberchk(C,Cs),
        D is X+Y, \+ memberchk(D,Ds),
        X1 is X + 1,
        test(Ys,X1,[C|Cs],[D|Ds]).

    %--------------------------------------------------------------

    % Now, in version 2, the tester is pushed completely inside the
    % generator permu.

    queens_2(N,Qs) :- range(1,N,Rs), permu_test(Rs,Qs,1,[],[]).

    permu_test([],[],_,_,_).
    permu_test(Qs,[Y|Ys],X,Cs,Ds) :-
        del(Y,Qs,Rs),
        C is X-Y, \+ memberchk(C,Cs),
        D is X+Y, \+ memberchk(D,Ds),
        X1 is X+1,
        permu_test(Rs,Ys,X1,[C|Cs],[D|Ds]).
    """
    N, Qs, N, Rs, Qs, A, B, L, A1, Y, Ys, X, Xs, Zs = Variable.factory(
        "N", "Qs", "N", "Rs", "Qs", "A", "B", "L", "A1", "Y", "Ys", "X", "Xs", "Zs"
    )
    _W1, _W2, _W3 = Variable.factory("_W1", "_W2", "_W3")
    Cs, Ds, D, X1, C, Cs = Variable.factory("Cs", "Ds", "D", "X1", "C", "Cs")

    db = [
        Rule(
            dict(queens_1=N, a=Qs),
            dict(range=1, a=N, b=Rs),
            dict(permu=Rs, a=Qs),
            dict(test=Qs),
        ),
        dict(range=A, a=A, b=[A]),
        Rule(
            dict(range=A, a=B, b=[A, *L]),
            Assert(lambda A, B: A < B),
            Assign(A1, lambda A: A + 1),
            dict(range=A1, a=B, b=L),
        ),
        dict(permu=[], a=[]),
        Rule(
            dict(permu=Qs, a=[Y, *Ys]), dict(delete=Y, a=Qs, b=Rs), dict(permu=Rs, a=Ys)
        ),
        dict(delete=X, a=[X, *Xs], b=Xs),
        Rule(dict(delete=X, a=[Y, *Ys], b=[Y, *Zs]), dict(delete=X, a=Ys, b=Zs)),
        Rule(dict(test=Qs), dict(test=Qs, a=1, b=[], c=[])),
        dict(test=[], a=_W1, b=_W2, c=_W3),
        Rule(
            dict(test=[Y, *Ys], a=X, b=Cs, c=Ds),
            Assign(C, lambda X, Y: X - Y),
            Assert(lambda C, Cs: C not in Cs),
            Assign(D, lambda X, Y: X + Y),
            Assert(lambda D, Ds: D not in Ds),
            Assign(X1, lambda X: X + 1),
            dict(test=Ys, a=X1, b=[C, *Cs], c=[D, *Ds]),
        ),
    ]
    Q = Variable("Q")
    query = dict(queens_1=8, a=Q)
    assert list(search(db, query)) == []
