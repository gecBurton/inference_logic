import pytest

from inference_logic import Rule, Variable
from inference_logic.algorithms import search
from inference_logic.data_structures import Assert, Assign, PrologList

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
    P03 (*): Find the K'th element of a list.
    The first element in the list is number 1.

    element_at(X,L,K) :- X is the K'th element of the list L
       (element,list,integer) (?,?,+)

    Note: nth1(?Index, ?List, ?Elem) is predefined

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
    P04 (*): Find the number of elements of a list.

    my_length(L,N) :- the list L contains N elements
       (list,integer) (+,?)

    Note: length(?List, ?Int) is predefined

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
    P05 (*): Reverse a list.

    my_reverse(L1,L2) :- L2 is the list obtained from L1 by reversing
       the order of the elements.
       (list,list) (?,?)

    Note: reverse(+List1, -List2) is predefined

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
    P06 (*): Find out whether a list is a palindrome
    A palindrome can be read forward or backward; e.g. [x,a,m,a,x]

    is_palindrome(L) :- L is a palindrome list
       (list) (?)

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
    P07 (**): Flatten a nested list structure.

    my_flatten(L1,L2) :- the list L2 is obtained from the list L1 by
       flattening; i.e. if an element of L1 is a list then it is replaced
       by its elements, recursively.
       (list,list) (+,?)

    Note: flatten(+List1, -List2) is a predefined predicate

    my_flatten(X,[X]) :- \\+ is_list(X).
    my_flatten([],[]).
    my_flatten([X|Xs],Zs) :- my_flatten(X,Y), my_flatten(Xs,Ys), append(Y,Ys,Zs).
    """
    assert False


def test_08():
    """
    P08 (**): Eliminate consecutive duplicates of list elements.

    compress(L1,L2) :- the list L2 is obtained from the list L1 by
       compressing repeated occurrences of elements into a single copy
       of the element.
       (list,list) (+,?)

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


def test_09():
    """
    P09 (**):  Pack consecutive duplicates of list elements into sublists.

    pack(L1,L2) :- the list L2 is obtained from the list L1 by packing
       repeated occurrences of elements into separate sublists.
       (list,list) (+,?)

    pack([],[]).
    pack([X|Xs],[Z|Zs]) :- transfer(X,Xs,Ys,Z), pack(Ys,Zs).

    transfer(X,Xs,Ys,Z) Ys is the list that remains from the list Xs
       when all leading copies of X are removed and transfered to Z

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
            dict(transfer=X, a=[Y, *Ys], b=[Y, *Ys], c=[X]),
            Assert(lambda X, Y: X != Y),
        ),
        Rule(
            dict(transfer=X, a=[X, *Xs], b=Ys, c=[X, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Zs),
        ),
    ]
    query = dict(pack=[1, 2, 2, 3, 3, 3], list=Q)
    assert list(search(db, query)) == [{Q: [[1], [2, 2], [3, 3, 3]]}]


def test_10():
    """
    P10 (*):  Run-length encoding of a list

    encode(L1,L2) :- the list L2 is obtained from the list L1 by run-length
       encoding. Consecutive duplicates of elements are encoded as terms [N,E],
       where N is the number of duplicates of the element E.
       (list,list) (+,?)

    :- ensure_loaded(p09).

    encode(L1,L2) :- pack(L1,L), transform(L,L2).

    transform([],[]).
    transform([[X|Xs]|Ys],[[N,X]|Zs]) :- length([X|Xs],N), transform(Ys,Zs).
    """
    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    L, L1, L2, N, N1 = Variable.factory("L", "L1", "L2", "N", "N1")

    db_04 = [
        dict(my_length=0, list=[]),
        Rule(
            dict(my_length=N, list=[_W, *L]),
            dict(my_length=N1, list=L),
            Assign(N, lambda N1: N1 + 1),
        ),
    ]

    db_09 = [
        dict(pack=[], list=[]),
        Rule(
            dict(pack=[X, *Xs], list=[Z, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Z),
            dict(pack=Ys, list=Zs),
        ),
        dict(transfer=X, a=[], b=[], c=[X]),
        Rule(
            dict(transfer=X, a=[Y, *Ys], b=[Y, *Ys], c=[X]),
            Assert(lambda X, Y: X != Y),
        ),
        Rule(
            dict(transfer=X, a=[X, *Xs], b=Ys, c=[X, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Zs),
        ),
    ]

    db_10 = [
        Rule(dict(encode=L1, a=L2), dict(pack=L1, list=L), dict(transform=L, list=L2)),
        dict(transform=[], list=[]),
        Rule(
            dict(transform=[[X, *Xs], *Ys], list=[[N, X], *Zs]),
            dict(my_length=N, list=[X, *Xs]),
            dict(transform=Ys, list=Zs),
        ),
    ]
    db = db_04 + db_09 + db_10
    query = dict(encode=[1, 2, 2, 3, 3, 3], a=Q)
    assert list(search(db, query)) == [{Q: [[1, 1], [2, 2], [3, 3]]}]


def test_11():
    """
    P11 (*):  Modified run-length encoding

    encode_modified(L1,L2) :- the list L2 is obtained from the list L1 by
       run-length encoding. Consecutive duplicates of elements are encoded
       as terms [N,E], where N is the number of duplicates of the element E.
       However, if N equals 1 then the element is simply copied into the
       output list.
       (list,list) (+,?)

    :- ensure_loaded(p10).

    encode_modified(L1,L2) :- encode(L1,L), strip(L,L2).

    strip([],[]).
    strip([[1,X]|Ys],[X|Zs]) :- strip(Ys,Zs).
    strip([[N,X]|Ys],[[N,X]|Zs]) :- N > 1, strip(Ys,Zs).
    """
    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    L, L1, L2, N, N1 = Variable.factory("L", "L1", "L2", "N", "N1")

    db_04 = [
        dict(my_length=0, list=[]),
        Rule(
            dict(my_length=N, list=[_W, *L]),
            dict(my_length=N1, list=L),
            Assign(N, lambda N1: N1 + 1),
        ),
    ]

    db_09 = [
        dict(pack=[], list=[]),
        Rule(
            dict(pack=[X, *Xs], list=[Z, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Z),
            dict(pack=Ys, list=Zs),
        ),
        dict(transfer=X, a=[], b=[], c=[X]),
        Rule(
            dict(transfer=X, a=[Y, *Ys], b=[Y, *Ys], c=[X]),
            Assert(lambda X, Y: X != Y),
        ),
        Rule(
            dict(transfer=X, a=[X, *Xs], b=Ys, c=[X, *Zs]),
            dict(transfer=X, a=Xs, b=Ys, c=Zs),
        ),
    ]

    db_10 = [
        Rule(dict(encode=L1, a=L2), dict(pack=L1, list=L), dict(transform=L, list=L2)),
        dict(transform=[], list=[]),
        Rule(
            dict(transform=[[X, *Xs], *Ys], list=[[N, X], *Zs]),
            dict(my_length=N, list=[X, *Xs]),
            dict(transform=Ys, list=Zs),
        ),
    ]

    db_11 = [
        Rule(
            dict(encode_modified=L1, list=L2),
            dict(encode=L1, a=L),
            dict(strip=L, list=L2),
        ),
        dict(strip=[], list=[]),
        Rule(dict(strip=[[1, X], *Ys], list=[X, *Zs]), dict(strip=Ys, list=Zs)),
        Rule(
            dict(strip=[[N, X], *Ys], list=[[N, X], *Zs]),
            Assert(lambda N: N > 1),
            dict(strip=Ys, list=Zs),
        ),
    ]
    db = db_04 + db_09 + db_10 + db_11
    query = dict(encode_modified=[1, 2, 2, 3, 3, 3], list=Q)
    assert list(search(db, query)) == [{Q: [1, [2, 2], [3, 3]]}]


@pytest.mark.xfail
def test_12():
    r"""
    P12 (**): Decode a run-length compressed list.

    decode(L1,L2) :- L2 is the uncompressed version of the run-length
       encoded list L1.
       (list,list) (+,?)

    decode([],[]).
    decode([X|Ys],[X|Zs]) :- \+ is_list(X), decode(Ys,Zs).
    decode([[1,X]|Ys],[X|Zs]) :- decode(Ys,Zs).
    decode([[N,X]|Ys],[X|Zs]) :- N > 1, N1 is N - 1, decode([[N1,X]|Ys],Zs).
    """
    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    N, N1 = Variable.factory("N", "N1")
    db = [
        dict(decode=[], list=[]),
        Rule(
            dict(decode=[X, *Ys], list=[X, *Zs]),
            Assert(lambda X: isinstance(X, PrologList)),
            dict(decode=Ys, list=Zs),
        ),
        Rule(dict(decode=[[1, X], *Ys], list=[X, *Zs]), dict(decode=Ys, list=Zs)),
        Rule(
            dict(decode=[[N, X], *Ys], list=[X, *Zs]),
            Assert(lambda N: N > 1),
            Assign(N1, lambda N: N - 1),
            dict(decode=[[N1, X], *Ys], list=Zs),
        ),
    ]
    query = dict(decode=[1, [2, 2], [3, 3]], list=Q)
    assert list(search(db, query)) == [{Q: [1, [2, 2], [3, 3]]}]


@pytest.mark.xfail
def test_13():
    r"""
    P13 (**): Run-length encoding of a list (direct solution)

    encode_direct(L1,L2) :- the list L2 is obtained from the list L1 by
       run-length encoding. Consecutive duplicates of elements are encoded
       as terms [N,E], where N is the number of duplicates of the element E.
       However, if N equals 1 then the element is simply copied into the
       output list.
       (list,list) (+,?)

    encode_direct([],[]).
    encode_direct([X|Xs],[Z|Zs]) :- count(X,Xs,Ys,1,Z), encode_direct(Ys,Zs).

    count(X,Xs,Ys,K,T) Ys is the list that remains from the list Xs
       when all leading copies of X are removed. T is the term [N,X],
       where N is K plus the number of X's that can be removed from Xs.
       In the case of N=1, T is X, instead of the term [1,X].

    count(X,[],[],1,X).
    count(X,[],[],N,[N,X]) :- N > 1.
    count(X,[Y|Ys],[Y|Ys],1,X) :- X \= Y.
    count(X,[Y|Ys],[Y|Ys],N,[N,X]) :- N > 1, X \= Y.
    count(X,[X|Xs],Ys,K,T) :- K1 is K + 1, count(X,Xs,Ys,K1,T).

    """
    Xs, Ys, Zs = Variable.factory("Xs", "Ys", "Zs")
    N, T, K, K1 = Variable.factory("N", "T", "K", "K1")

    db = [
        dict(encode_direct=[], list=[]),
        Rule(
            dict(encode_direct=[X, *Xs], list=[Z, *Zs]),
            dict(count=X, a=Xs, b=Ys, c=1, d=Z),
            dict(encode_direct=Ys, list=Zs),
        ),
        dict(count=X, a=[], b=[], c=1, d=X),
        Rule(dict(count=X, a=[], b=[], c=N, d=[N, X]), Assert(lambda N: N > 1)),
        Rule(
            dict(count=X, a=[Y, *Ys], b=[Y, *Ys], c=1, d=X), Assert(lambda X, Y: X != Y)
        ),
        Rule(
            dict(count=X, a=[Y, *Ys], b=[Y, *Ys], c=N, d=[N, X]),
            Assert(lambda N: N > 1),
            Assert(lambda X, Y: X != Y),
        ),
        Rule(
            dict(count=X, a=[X, *Xs], b=Ys, c=K, d=T),
            Assign(K1, lambda K: K + 1),
            dict(coun=X, a=Xs, b=Ys, c=K1, d=T),
        ),
    ]
    query = dict(count=6, a=[6, 6, 6, 6, 7], b=Ys, c=2, d=6)
    # query = dict(encode_direct=[1, 2, 2, 3, 3, 3], list=Q)
    assert list(search(db, query)) == [{Q: [1, [2, 2], [3, 3]]}]


def test_14():
    """
    P14 (*): Duplicate the elements of a list

    dupli(L1,L2) :- L2 is obtained from L1 by duplicating all elements.
       (list,list) (?,?)

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


def test_15():
    """
    P15 (**): Duplicate the elements of a list agiven number of times

    dupli(L1,N,L2) :- L2 is obtained from L1 by duplicating all elements
       N times.
       (list,integer,list) (?,+,?)

    dupli(L1,N,L2) :- dupli(L1,N,L2,N).

    dupli(L1,N,L2,K) :- L2 is obtained from L1 by duplicating its leading
       element K times, all other elements N times.
       (list,integer,list,integer) (?,+,?,+)

    dupli([],_,[],_).
    dupli([_|Xs],N,Ys,0) :- dupli(Xs,N,Ys,N).
    dupli([X|Xs],N,[X|Ys],K) :- K > 0, K1 is K - 1, dupli([X|Xs],N,Ys,K1).
    """
    Xs, N, Ys, K, K1 = Variable.factory("Xs", "N", "Ys", "K", "K1")
    L1, L2 = Variable.factory("L1", "L2")
    db = [
        dict(dupli=[], a=_W, b=[], c=_W),
        Rule(dict(dupli=[_W, *Xs], a=N, b=Ys, c=0), dict(dupli=Xs, a=N, b=Ys, c=N)),
        Rule(
            dict(dupli=[X, *Xs], a=N, b=[X, *Ys], c=K),
            Assert(lambda K: K > 0),
            Assign(K1, lambda K: K - 1),
            dict(dupli=[X, *Xs], a=N, b=Ys, c=K1),
        ),
        Rule(dict(dupli=L1, a=N, b=L2), dict(dupli=L1, a=N, b=L2, c=N)),
    ]
    assert list(search(db, dict(dupli=[1, 2], a=2, b=Q))) == [{Q: [1, 1, 2, 2]}]


def test_16():
    """
    P16 (**):  Drop every N'th element from a list

    drop(L1,N,L2) :- L2 is obtained from L1 by dropping every N'th element.
       (list,integer,list) (?,+,?)

    drop(L1,N,L2) :- drop(L1,N,L2,N).

    drop(L1,N,L2,K) :- L2 is obtained from L1 by first copying K-1 elements
       and then dropping an element and, from then on, dropping every
       N'th element.
       (list,integer,list,integer) (?,+,?,+)

    drop([],_,[],_).
    drop([_|Xs],N,Ys,1) :- drop(Xs,N,Ys,N).
    drop([X|Xs],N,[X|Ys],K) :- K > 1, K1 is K - 1, drop(Xs,N,Ys,K1).
    """
    Xs, Ys, N, K, K1, Q = Variable.factory("Xs", "Ys", "N", "K", "K1", "Q")
    L1, L2 = Variable.factory("L1", "L2")
    db = [
        dict(drop=[], a=_W, b=[], c=_W),
        Rule(dict(drop=[_W, *Xs], a=N, b=Ys, c=1), dict(drop=Xs, a=N, b=Ys, c=N)),
        Rule(
            dict(drop=[X, *Xs], a=N, b=[X, *Ys], c=K),
            Assert(lambda K: K > 1),
            Assign(K1, lambda K: K - 1),
            dict(drop=Xs, a=N, b=Ys, c=K1),
        ),
        Rule(dict(drop=L1, a=N, b=L2), dict(drop=L1, a=N, b=L2, c=N)),
    ]
    assert list(search(db, dict(drop=[1, 2, 3, 4, 5, 6, 7, 8, 9], a=3, b=Q))) == [
        {Q: [1, 2, 4, 5, 7, 8]}
    ]


def test_17():
    """
    P17 (*): Split a list into two parts

    split(L,N,L1,L2) :- the list L1 contains the first N elements
       of the list L, the list L2 contains the remaining elements.
       (list,integer,list,list) (?,+,?,?)

    split(L,0,[],L).
    split([X|Xs],N,[X|Ys],Zs) :- N > 0, N1 is N - 1, split(Xs,N1,Ys,Zs).
    """
    X, Xs, Ys, Zs, N, N1, P, Q = Variable.factory(
        "X", "Xs", "Ys", "Zs", "N", "N1", "P", "Q"
    )
    db = [
        dict(split=L, a=0, b=[], c=L),
        Rule(
            dict(split=[X, *Xs], a=N, b=[X, *Ys], c=Zs),
            Assert(lambda N: N > 0),
            Assign(N1, lambda N: N - 1),
            dict(split=Xs, a=N1, b=Ys, c=Zs),
        ),
    ]
    assert list(search(db, dict(split=[1, 2, 3, 4, 5, 6, 7, 8], a=3, b=Q, c=P))) == [
        {Q: [1, 2, 3], P: [4, 5, 6, 7, 8]}
    ]


@pytest.mark.xfail
def test_18():
    assert False


@pytest.mark.xfail
def test_19():
    assert False


@pytest.mark.xfail
def test_20():
    assert False


@pytest.mark.xfail
def test_21():
    assert False


def test_22():
    """
    P22 (*):  Create a list containing all integers within a given range.

    range(I,K,L) :- I <= K, and L is the list containing all
       consecutive integers from I to K.
       (integer,integer,list) (+,+,?)

    range(I,I,[I]).
    range(I,K,[I|L]) :- I < K, I1 is I + 1, range(I1,K,L).
    """
    I, I1, K, L = Variable.factory("I", "I1", "K", "L")
    db = [
        dict(start=I, end=I, list=[I]),
        Rule(
            dict(start=I, end=K, list=[I, *L]),
            Assert(lambda I, K: I < K),
            Assign(I1, lambda I: I + 1),
            dict(start=I1, end=K, list=L),
        ),
    ]
    query = dict(start=2, end=5, list=Z)
    assert list(search(db, query)) == [{Z: [2, 3, 4, 5]}]


def test_26():
    """
    P26 (**):  Generate the combinations of k distinct objects
               chosen from the n elements of a list.

    combination(K,L,C) :- C is a list of K distinct elements
       chosen from the list L

    combination(0,_,[]).
    combination(K,L,[X|Xs]) :- K > 0,
    el(X,L,R), K1 is K-1, combination(K1,R,Xs).

    Find out what the following predicate el/3 exactly does.

    el(X,[X|L],L).
    el(X,[_|L],R) :- el(X,L,R).
    """
    R, K, K1, Xs = Variable.factory("R", "K", "K1", "Xs")
    db = [
        dict(el=X, a=[X, *L], b=L),
        Rule(dict(el=X, a=[_W, *L], b=R), dict(el=X, a=L, b=R)),
        dict(choose=0, initial=_W, result=[]),
        Rule(
            dict(choose=K, initial=L, result=[X, *Xs]),
            Assert(lambda K: K > 0),
            dict(el=X, a=L, b=R),
            Assign(K1, lambda K: K - 1),
            dict(choose=K1, initial=R, result=Xs),
        ),
    ]

    query = dict(choose=2, initial=[1, 2, 3], result=Q)
    assert list(search(db, query)) == [{Q: [2, 3]}, {Q: [1, 3]}, {Q: [1, 2]}]


@pytest.mark.xfail
def test_27():
    assert False


@pytest.mark.xfail
def test_28():
    assert False
