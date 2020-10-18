from itertools import product
from typing import Any, Dict, Iterator, List, Optional, Tuple

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


def unify(left, right, equality: Optional[Equality] = None) -> Equality:
    left, right = construct(left), construct(right)

    equality = Equality() if equality is None else equality

    if isinstance(left, ImmutableDict) and isinstance(right, ImmutableDict):
        if left.keys() != right.keys():
            raise UnificationError(f"keys must match: {tuple(left)} != {tuple(right)}")
        for key in left.keys():
            equality = unify(left[key], right[key], equality)
        return equality

    if isinstance(left, PrologList) and isinstance(right, PrologList):
        equality = unify(left.head, right.head, equality)
        equality = unify(left.tail, right.tail, equality)
        return equality

    if isinstance(left, PrologList) and isinstance(right, PrologListNull):
        raise UnificationError("list lengths must be the same")
    if isinstance(left, PrologListNull) and isinstance(right, PrologList):
        raise UnificationError("list lengths must be the same")

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
