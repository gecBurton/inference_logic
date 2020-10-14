"""https://www.ic.unicamp.br/~meidanis/courses/mc336/2009s2/prolog/problemas/
"""
import pytest

from json_inference_logic import Rule, Variable
from json_inference_logic.algorithms import search
from json_inference_logic.data_structures import Assert, Assign

X, Y, Z = Variable.factory("X", "Y", "Z")
L, _W = Variable.factory("L", "W")
Q = Variable("Q")


def test_01():
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


def test_02():
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


def test_03():
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


def test_04():
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


def test_05():
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


def test_06():
    """
    % P06 (*): Find out whether a list is a palindrome
    % A palindrome can be read forward or backward; e.g. [x,a,m,a,x]

    % is_palindrome(L) :- L is a palindrome list
    %    (list) (?)

    is_palindrome(L) :- reverse(L,L).
    """
    L1, L2, Xs, Acc = Variable.factory("L1", "L2", "Xs", "Acc")
    db = [
        dict(my_rev=[], a=L2, b=L2),
        Rule(dict(my_rev=[X, *Xs], a=L2, b=Acc), dict(my_rev=Xs, a=L2, b=[X, *Acc])),
        Rule(dict(is_palindrome=X), dict(my_rev=X, a=X, b=[])),
    ]
    query = dict(is_palindrome=[1, 2, 1])
    assert list(search(db, query)) == [{}]


@pytest.mark.xfail()
def test_07():
    """
    % P07 (**): Flatten a nested list structure.

    % my_flatten(L1,L2) :- the list L2 is obtained from the list L1 by
    %    flattening; i.e. if an element of L1 is a list then it is replaced
    %    by its elements, recursively.
    %    (list,list) (+,?)

    % Note: flatten(+List1, -List2) is a predefined predicate

    my_flatten(X,[X]) :- \\+ is_list(X).
    my_flatten([],[]).
    my_flatten([X|Xs],Zs) :- my_flatten(X,Y), my_flatten(Xs,Ys), append(Y,Ys,Zs).
    """
    assert False


def test_08():
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
    query = dict(compress=[1, 2, 1], list=Q)
    out = list(search(db, query))
    assert out == [{Q: [1, 2, 1]}]


@pytest.mark.xfail
def test_09():
    """
    % P09 (**):  Pack consecutive duplicates of list elements into sublists.

    % pack(L1,L2) :- the list L2 is obtained from the list L1 by packing
    %    repeated occurrences of elements into separate sublists.
    %    (list,list) (+,?)

    pack([],[]).
    pack([X|Xs],[Z|Zs]) :- transfer(X,Xs,Ys,Z), pack(Ys,Zs).

    % transfer(X,Xs,Ys,Z) Ys is the list that remains from the list Xs
    %    when all leading copies of X are removed and transfered to Z

    transfer(X,[],[],[X]).
    transfer(X,[Y|Ys],[Y|Ys],[X]) :- X \\= Y.
    transfer(X,[X|Xs],Ys,[X|Zs]) :- transfer(X,Xs,Ys,Zs).
    """

    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    db = [
        dict(pack=[], list=[]),
        Rule(
            dict(pack=[X, *Xs], list=[Z, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Z),
            dict(pack=Ys, list=Zs),
        ),
        dict(transfer=X, a=[], b=[], c=[X]),
        Rule(
            dict(transfer=[X], a=[Y, *Ys], b=[Y, *Ys], c=[X]),
            Assert(lambda X, Y: X != Y),
        ),
        Rule(
            dict(transfer=X, a=[X, *Xs], b=Ys, c=[X, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Zs),
        ),
    ]
    query = dict(transfer=1, a=[1, 1, 1, 1, 1, 2], b=[2], c=Variable("QQ"))
    assert list(search(db, query)) == [{Q: [[1], [2]]}]


def test_14():
    """
    % P14 (*): Duplicate the elements of a list

    % dupli(L1,L2) :- L2 is obtained from L1 by duplicating all elements.
    %    (list,list) (?,?)

    dupli([],[]).
    dupli([X|Xs],[X,X|Ys]) :- dupli(Xs,Ys).
    """
    Xs, Ys = Variable.factory("Xs", "Ys")

    db = [
        dict(dupli=[], list=[]),
        Rule(dict(dupli=[X, *Xs], list=[X, X, *Ys]), dict(dupli=Xs, list=Ys)),
    ]

    query = dict(dupli=["a", "b"], list=Z)

    assert list(search(db, query)) == [{Z: ["a", "a", "b", "b"]}]


def test_22():
    """
    % P22 (*):  Create a list containing all integers within a given range.

    % range(I,K,L) :- I <= K, and L is the list containing all
    %    consecutive integers from I to K.
    %    (integer,integer,list) (+,+,?)

    range(I,I,[I]).
    range(I,K,[I|L]) :- I < K, I1 is I + 1, range(I1,K,L).
    """
    I, I1, K, L = Variable.factory("I", "I1", "K", "L")
    db = [
        dict(arrange=I, a=I, b=[I]),
        Rule(
            dict(arrange=I, a=K, b=[I, *L]),
            Assert(lambda I, K: I < K),
            Assign(I1, lambda I: I + 1),
            dict(arrange=I1, a=K, b=L),
        ),
    ]
    query = dict(arrange=2, a=5, b=Z)
    assert list(search(db, query)) == [{Z: [2, 3, 4, 5]}]


def test_26():
    """
    % P26 (**):  Generate the combinations of k distinct objects
    %            chosen from the n elements of a list.

    % combination(K,L,C) :- C is a list of K distinct elements
    %    chosen from the list L

    combination(0,_,[]).
    combination(K,L,[X|Xs]) :- K > 0,
    el(X,L,R), K1 is K-1, combination(K1,R,Xs).

    % Find out what the following predicate el/3 exactly does.

    el(X,[X|L],L).
    el(X,[_|L],R) :- el(X,L,R).
    """
    R, K, K1, Xs = Variable.factory("R", "K", "K1", "Xs")
    db = [
        dict(el=X, a=[X, *L], b=L),
        Rule(dict(el=X, a=[_W, *L], b=R), dict(el=X, a=L, b=R)),
        dict(combination=0, a=_W, b=[]),
        Rule(
            dict(combination=K, a=L, b=[X, *Xs]),
            Assert(lambda K: K > 0),
            dict(el=X, a=L, b=R),
            Assign(K1, lambda K: K - 1),
            dict(combination=K1, a=R, b=Xs),
        ),
    ]

    query = dict(combination=2, a=[1, 2, 3], b=Q)
    assert list(search(db, query)) == [{Q: [2, 3]}, {Q: [1, 3]}, {Q: [1, 2]}]
