"""https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
"""

from json_inference_logic import Equality, Rule, Variable
from json_inference_logic.algorithms import search
from json_inference_logic.data_structures import Assign

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
        dict(last=X, list=(X,)),
        Rule(dict(last=X, list=(_W, *L)), dict(last=X, list=L)),
    ]

    query = dict(last=Q, list=("a", "b", "c"))
    assert next(search(db, query)) == Equality(fixed={"c": {Q}})


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
    assert next(search(db, query)) == Equality(fixed={"b": {Q}})


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
    assert next(search(db, query)) == Equality(fixed={3: {Q}})
