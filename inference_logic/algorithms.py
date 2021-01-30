from itertools import product
from typing import Any, Dict, Iterator, List, Tuple

from inference_logic.data_structures import (
    Assert,
    Assign,
    ImmutableDict,
    Rule,
    UnificationError,
    Variable,
    construct,
    get_variables,
    new_frame,
)
from inference_logic.equality import Equality


def search(db: List, query: ImmutableDict) -> Iterator[Dict[Variable, Any]]:
    query = construct(query)

    i = 0
    to_solve_for = get_variables(query)

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
                if not isinstance(rule, Rule):
                    rule = Rule(rule)
                i += 1
                rule = new_frame(rule, i)

                try:
                    new_known = equality.unify(goal.predicate, rule.predicate)

                    new_terms: Iterator[Iterator] = filter(
                        None,
                        product(
                            *tuple(
                                new_known.inject(term, to_solve_for=to_solve_for)
                                for term in rule.body + goal.body
                            )
                        ),
                    )

                    for terms in new_terms:
                        stack.append((Rule(*terms), new_known))

                    solutions = new_known.solutions(to_solve_for)

                    if (
                        not goal.body
                        and not rule.body
                        and set(solutions) == to_solve_for
                    ):
                        yield solutions

                except UnificationError:
                    pass
