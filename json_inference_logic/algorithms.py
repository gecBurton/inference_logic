from itertools import product
from typing import Any, Dict, Iterator, List, Optional, Tuple

from json_inference_logic.data_structures import (
    Assert,
    Assign,
    ImmutableDict,
    PrologList,
    Rule,
    UnificationError,
    Variable,
    construct,
)
from json_inference_logic.equality import Equality


def new_frame(obj, frame: int):
    obj = construct(obj)
    if isinstance(obj, Rule):
        return Rule(
            new_frame(obj.predicate, frame), *(new_frame(o, frame) for o in obj.body),
        )
    if isinstance(obj, PrologList):
        return PrologList(new_frame(obj.head, frame), new_frame(obj.tail, frame))
    if isinstance(obj, ImmutableDict):
        return ImmutableDict(**{k: new_frame(v, frame) for k, v in obj.items()})
    if isinstance(obj, (Assign, Variable, Assert)):
        return obj.new_frame(frame)
    return obj


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
                rule = new_frame(rule, i)

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
