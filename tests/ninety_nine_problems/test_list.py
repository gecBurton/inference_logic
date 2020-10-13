"""https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
"""
import pytest

from json_inference_logic import Rule, Variable
from json_inference_logic.algorithms import search
from json_inference_logic.data_structures import Assert, Assign

X, Y, Z = Variable.factory("X", "Y", "Z")
L, _W = Variable.factory("L", "W")
Q = Variable("Q")


def test_find_the_last_element_of_a_list_01():
    """
    P01 (*): Find the last element of a list

    my_last(X,L) :- X is the last element of the list L
       (element,list) (?,?)

    Note: last(?Elem, ?List) is predefined

    my_last(X,[X]).
    my_last(X,[_|L]) :- my_last(X,L).
    """

    db = [
        dict(last=X, list=[X]),
        Rule(dict(last=X, list=[_W, *L]), dict(last=X, list=L)),
    ]

    query = dict(last=Q, list=["a", "b", "c"])
    assert list(search(db, query)) == [{Q: "c"}]


def test_find_the_last_but_one_element_of_a_list_02():
    """
    P02 (*): Find the last but one element of a list

    last_but_one(X,L) :- X is the last but one element of the list L
       (element,list) (?,?)

    last_but_one(X,[X,_]).
    last_but_one(X,[_,Y|Ys]) :- last_but_one(X,[Y|Ys]).
    """
    Ys = Variable("Ys")

    db = [
        dict(last_but_one=X, list=(X, _W)),
        Rule(
            dict(last_but_one=X, list=(_W, Y, *Ys)),
            dict(last_but_one=X, list=(Y, *Ys)),
        ),
    ]
    query = dict(last_but_one=Q, list=["a", "b", "c"])
    assert next(search(db, query)) == {Q: "b"}


def test_find_the_kth_element_of_a_list_03():
    """
    % P03 (*): Find the K'th element of a list.
    % The first element in the list is number 1.

    % element_at(X,L,K) :- X is the K'th element of the list L
    %    (element,list,integer) (?,?,+)

    % Note: nth1(?Index, ?List, ?Elem) is predefined

    element_at(X,[X|_],1).
    element_at(X,[_|L],K) :- K > 1, K1 is K - 1, element_at(X,L,K1).
    """
    K, K1 = Variable.factory("K", "K1")

    db = [
        dict(nth_element=X, list=(X, *_W), n=1),
        Rule(
            dict(nth_element=X, list=(_W, *L), n=K),
            Assert(lambda K: K > 1),
            Assign(K1, lambda K: K - 1),
            dict(nth_element=X, list=L, n=K1),
        ),
    ]
    query_1 = dict(nth_element=Z, list=["a", "b", "c"], n=1)
    assert list(search(db, query_1)) == [{Z: "a"}]

    query_2 = dict(nth_element=Z, list=["a", "b", "c"], n=2)
    assert list(search(db, query_2)) == [{Z: "b"}]


def test_find_the_number_of_elements_of_a_list_04():
    """
    % P04 (*): Find the number of elements of a list.

    % my_length(L,N) :- the list L contains N elements
    %    (list,integer) (+,?)

    % Note: length(?List, ?Int) is predefined

    my_length([],0).
    my_length([_|L],N) :- my_length(L,N1), N is N1 + 1.
    """
    N, N1 = Variable.factory("N", "N1")
    db = [
        dict(my_length=0, list=[]),
        Rule(
            dict(my_length=N, list=[_W, *L]),
            dict(my_length=N1, list=L),
            Assign(N, lambda N1: N1 + 1),
        ),
    ]
    query = dict(my_length=Q, list=[1, 2, 3])
    assert list(search(db, query)) == [{Q: 3}]


def test_reverse_a_list_05():
    """
    % P05 (*): Reverse a list.

    % my_reverse(L1,L2) :- L2 is the list obtained from L1 by reversing
    %    the order of the elements.
    %    (list,list) (?,?)

    % Note: reverse(+List1, -List2) is predefined

    my_reverse(L1,L2) :- my_rev(L1,L2,[]).

    my_rev([],L2,L2) :- !.
    my_rev([X|Xs],L2,Acc) :- my_rev(Xs,L2,[X|Acc]).
    """
    L1, L2, Xs, Acc = Variable.factory("L1", "L2", "Xs", "Acc")
    db = [
        dict(my_rev=[], list_in=L2, list_out=L2),
        Rule(
            dict(my_rev=[X, *Xs], list_in=L2, list_out=Acc),
            dict(my_rev=Xs, list_in=L2, list_out=[X, *Acc]),
        ),
    ]
    query = dict(my_rev=[1, 2], list_in=Z, list_out=[])
    assert list(search(db, query)) == [{Z: [2, 1]}]


@pytest.mark.xfail
def test_eliminate_consecutive_duplicates_of_list_elements_08():
    """
    % P08 (**): Eliminate consecutive duplicates of list elements.

    % compress(L1,L2) :- the list L2 is obtained from the list L1 by
    %    compressing repeated occurrences of elements into a single copy
    %    of the element.
    %    (list,list) (+,?)

    compress([],[]).
    compress([X],[X]).
    compress([X,X|Xs],Zs) :- compress([X|Xs],Zs).
    compress([X,Y|Ys],[X|Zs]) :- X \\= Y, compress([Y|Ys],Zs).
    """
    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    db = [
        dict(compress=[], list=[]),
        dict(compress=[X], list=[X]),
        Rule(dict(compress=[X, X, *Xs], list=Zs), dict(compress=[X, *Xs], list=Zs)),
        Rule(
            dict(compress=[X, Y, *Ys], list=[X, *Zs]),
            Assert(lambda X, Y: X != Y),
            dict(compress=[Y, *Ys], list=Zs),
        ),
    ]
    query = dict(compress=[1, 1, 2, 3, 2], list=Z)
    out = list(search(db, query))
    assert out == [{Z: (1, 2, 3, 2)}]
