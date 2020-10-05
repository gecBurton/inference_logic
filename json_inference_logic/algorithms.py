from itertools import product
from typing import Iterator, List, Optional

from json_inference_logic.data_structures import (
    Assign,
    ImmutableDict,
    Rule,
    UnificationError,
    Variable,
)
from json_inference_logic.equality import Equality, Goal


def new_frame(obj, frame: int):
    if isinstance(obj, Rule):
        return Rule(new_frame(obj.head, frame), *new_frame(obj.body, frame),)
    if isinstance(obj, tuple):
        return tuple(new_frame(o, frame) for o in obj)
    if isinstance(obj, ImmutableDict):
        return ImmutableDict(**{k: new_frame(v, frame) for k, v in obj.items()})
    if isinstance(obj, Variable):
        return obj.new_frame(frame)
    if isinstance(obj, Assign):
        return Assign(obj.variable, obj.expression, frame)
    return obj


def unify(left, right, equality: Optional[Equality] = None) -> Equality:
    equality = Equality() if equality is None else equality

    if isinstance(left, ImmutableDict) and isinstance(right, ImmutableDict):
        if left.keys() != right.keys():
            raise UnificationError(f"keys must match: {tuple(left)} != {tuple(right)}")
        for key in left.keys():
            equality = unify(left[key], right[key], equality)
        return equality

    if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):

        if left and isinstance(left[-1], Variable) and left[-1].many:
            n = len(left) - 1
            _equality = unify(left[:n], right[:n], equality=equality)
            return unify(left[-1], right[n:], equality=_equality)

        if right and isinstance(right[-1], Variable) and right[-1].many:
            n = len(right) - 1
            _equality = unify(left[:n], right[:n], equality=equality)
            return unify(left[n:], right[-1], equality=_equality)

        if len(left) != len(right):
            raise UnificationError(
                f"tuples must have same length: {len(left)} != {len(right)}"
            )
        for left_item, right_item in zip(left, right):
            equality = unify(left_item, right_item, equality)
        return equality

    return equality.add(left, right)


def search(db: List, query: ImmutableDict) -> Iterator[Equality]:
    db = [Rule(item) if not isinstance(item, Rule) else item for item in db]

    i = 0
    to_solve_for = query.get_variables()

    stack = [Goal(query)]

    while stack:
        goal = stack.pop()

        if isinstance(goal.head, Assign):
            if goal.tail:
                stack.append(goal.assign_next())
            else:
                yield goal.solve(to_solve_for)
        else:
            for rule in db:
                i += 1
                rule = new_frame(rule, i)

                try:
                    new_known = unify(goal.head, rule.head, equality=goal.equality)

                    new_terms: Iterator[Iterator] = filter(
                        None,
                        product(
                            *tuple(
                                new_known.inject(term, to_solve_for=to_solve_for)
                                for term in rule.body + goal.tail
                            )
                        ),
                    )

                    for x in new_terms:
                        stack.append(Goal(*x, equality=new_known))

                    solutions = new_known.solutions(to_solve_for)

                    if (
                        not goal.tail
                        and not rule.body
                        # and solutions.get_variables() == to_solve_for
                    ):
                        yield solutions

                except UnificationError:
                    pass
