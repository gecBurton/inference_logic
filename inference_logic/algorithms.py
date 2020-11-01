from itertools import product
from typing import Any, Dict, Iterator, List, Tuple

from multipledispatch import dispatch

from inference_logic.data_structures import (
    Assert,
    Assign,
    ImmutableDict,
    PrologList,
    PrologListNull,
    Rule,
    UnificationError,
    Variable,
    construct,
)
from inference_logic.equality import Equality


@dispatch(ImmutableDict, ImmutableDict, equality=Equality)  # type: ignore
def unify(left, right, equality: Equality) -> Equality:
    if left.keys() != right.keys():
        raise UnificationError(f"keys must match: {tuple(left)} != {tuple(right)}")
    for key in left.keys():
        equality = unify(left[key], right[key], equality=equality)
    return equality


@dispatch(PrologList, PrologList, equality=Equality)  # type: ignore
def unify(left, right, equality: Equality) -> Equality:
    equality = unify(left.head, right.head, equality=equality)
    equality = unify(left.tail, right.tail, equality=equality)
    return equality


@dispatch(PrologList, PrologListNull, equality=Equality)  # type: ignore
def unify(left, right, equality: Equality) -> Equality:
    raise UnificationError("list lengths must be the same")


@dispatch(PrologListNull, PrologList, equality=Equality)  # type: ignore
def unify(left, right, equality: Equality) -> Equality:
    raise UnificationError("list lengths must be the same")


@dispatch(object, object, equality=Equality)  # type: ignore
def unify(left, right, equality: Equality) -> Equality:
    """
    Unification is a key idea in declarative programming.
    https://en.wikipedia.org/wiki/Unification_(computer_science)

    This function has 3 tasks:

    1. Unification of values:

        >>> A, B, C = Variable.factory("A", "B", "C")

        When two primitive values are unified it will check that they are
        equal to each other, and return an empty Equality object.

        >>> unify(1, 1)
        .

        >>> unify(True, False)
        Traceback (most recent call last):
            ...
        inference_logic.data_structures.UnificationError: values dont match: True != False

        or fails with a UnificationError if they are not.

        If a Variable is passed as an argument then this variable will be set
        equal to the other vale which could either be, a primitive:

        >>> unify(True, B)
        True: {B}

        Or another varible

        >>> unify(A, B)
        {A, B}


    2. Unification against know Equalities:

        Unification operations can be chained together by passing in
        an optional equality argument.

        This way unified Variables can be assigned to existing
        Variable Sets

        >>> unify(A, C, Equality(free=[{A, B}]))
        {A, B, C}

        or constants.

        >>> unify(A, 1, Equality(free=[{A, B}]))
        1: {A, B}

        And we can check for consistencey between uunifications.

        >>> unify(B, False, Equality(fixed={True: {A, B}}))
        Traceback (most recent call last):
            ...
        inference_logic.data_structures.UnificationError: B cannot equal False because False != True


    3. Unification of Structure:

        When compound data structures, dicts and tuples, are unified then the
        unification first checks that the data-structures have the same type,
        any then is applied pair-wise and recursively to all elements.

        >>> unify(dict(a=A, b=2), dict(a=1, b=B))
        1: {A}, 2: {B}

        >>> unify((A, B), (1, 2))
        1: {A}, 2: {B}

        In the case of dicts the unification will fail if the keys do not match:

        >>> unify(dict(a=1, b=2), dict(a=1, c=2))
        Traceback (most recent call last):
            ...
        inference_logic.data_structures.UnificationError: keys must match: ('a', 'b') != ('a', 'c')

        And tuple unification will fail if they have different lengths

        >>> unify((A, B), (1, 2, 3))
        Traceback (most recent call last):
            ...
        inference_logic.data_structures.UnificationError: list lengths must be the same

        It possible to unify some Variables to the head of a tuple and another to the rest
        using the * syntax

        >>> unify((A, B, *C), (1, 2, 3, 4))
        1: {A}, 2: {B}, [3, 4]: {C}

    """

    return equality.add(left, right)


def search(db: List, query: ImmutableDict) -> Iterator[Dict[Variable, Any]]:
    db = [Rule(item) if not isinstance(item, Rule) else item for item in db]
    query = construct(query)

    i = 0
    to_solve_for = query.get_variables()

    stack: List[Tuple[Rule, Equality]] = [(Rule(query), Equality())]

    while stack:
        goal, equality = stack.pop()

        if isinstance(goal.predicate, (Assign, Assert)):
            try:
                equality = equality.evaluate(goal.predicate)
                if goal.body:
                    stack.append((Rule(*goal.body), equality))
                else:
                    yield equality.solutions(to_solve_for)
            except UnificationError:
                pass
        else:
            for rule in db:
                i += 1
                rule = rule.new_frame(i)

                try:
                    new_known = unify(goal.predicate, rule.predicate, equality=equality)

                    new_terms: Iterator[Iterator] = filter(
                        None,
                        product(
                            *tuple(
                                new_known.inject(term, to_solve_for=to_solve_for)
                                for term in rule.body + goal.body
                            )
                        ),
                    )

                    for x in new_terms:
                        stack.append((Rule(*x), new_known))

                    solutions = new_known.solutions(to_solve_for)

                    if (
                        not goal.body
                        and not rule.body
                        # and solutions.get_variables() == to_solve_for
                    ):
                        yield solutions

                except UnificationError:
                    pass
