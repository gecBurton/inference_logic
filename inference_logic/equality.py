from __future__ import annotations

from copy import deepcopy
from itertools import product
from typing import Any, Dict, List, Optional, Sequence, Set, Union

from inference_logic.data_structures import (
    Assert,
    Assign,
    ImmutableDict,
    PrologList,
    UnificationError,
    Variable,
    construct,
    deconstruct,
)


class Equality:
    def __init__(
        self,
        free: Sequence[Set[Variable]] = None,
        fixed: Dict[Union[Any, ImmutableDict], Set[Variable]] = None,
    ) -> None:
        self.fixed: Dict[ImmutableDict, Set[Variable]] = {}
        for constant, variable_set in (fixed or {}).items():
            self.fixed[constant] = variable_set.copy()
        self.free: List[Set[Variable]] = [
            variable_set.copy() for variable_set in free or []
        ]

    def __repr__(self) -> str:
        fixed = ", ".join(f"{k}={v}" for k, v in self.fixed.items())
        free = ", ".join(map(str, self.free))
        return f"Equality({free}, {fixed})"

    def __hash__(self) -> int:
        free = hash(tuple(map(Variable.hash_set, self.free)))
        fixed = hash(
            tuple(
                hash((constant, Variable.hash_set(self.fixed[constant])))
                for constant in sorted(self.fixed, key=hash)
            )
        )
        return free ^ fixed

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Equality):
            raise TypeError(f"{other} must be an Equality")
        return hash(self) == hash(other)

    def get_free(self, variable: Variable) -> Set[Variable]:
        if not isinstance(variable, Variable):
            raise TypeError(f"{variable} must be a Variable")
        for variables in self.free:
            if variable in variables:
                return variables
        return set()

    def get_fixed(self, variable: Variable) -> Any:
        if not isinstance(variable, Variable):
            raise TypeError(f"{variable} must be a Variable")
        for _variable in self.get_free(variable) | {variable}:
            for constant, variables in self.fixed.items():
                if _variable in variables:
                    return constant

        raise KeyError

    def get_deep(self, item):
        if isinstance(item, Variable):
            return self.get_deep(self.get_fixed(item))
        elif isinstance(item, ImmutableDict):
            return ImmutableDict(
                {key: self.get_deep(value) for key, value in item.items()}
            )
        elif isinstance(item, PrologList):
            try:
                return PrologList(self.get_deep(item.head), self.get_deep(item.tail))
            except RecursionError:
                raise
        return item

    def _add_constant(self, variable: Variable, constant: Any) -> Equality:
        if not isinstance(variable, Variable):
            raise TypeError(f"{variable} must be a Variable")
        if isinstance(constant, Variable):
            raise TypeError(f"{constant} may not be a Variable")
        try:
            hash(constant)
        except TypeError:
            raise TypeError(f"{constant} must be hashable")

        try:
            fixed = self.get_fixed(variable)

            if constant != fixed:
                raise UnificationError(
                    f"{variable} cannot equal {constant} because {constant} != {fixed}"
                )
            return self
        except KeyError:
            pass

        free = self.get_free(variable)
        out_free, out_fixed = deepcopy(self.free), deepcopy(self.fixed)
        if free:
            out_free.remove(free)
            if constant not in out_fixed:
                out_fixed[constant] = set()
            out_fixed[constant].update(free)
        else:
            if constant not in out_fixed:
                out_fixed[constant] = set()
            out_fixed[constant].add(variable)
        return Equality(out_free, out_fixed)

    def _add_variable(self, left: Variable, right: Variable) -> Equality:
        if not isinstance(left, Variable):
            raise TypeError(f"{left} must be a Variable")
        if not isinstance(right, Variable):
            raise TypeError(f"{right} must be a Variable")

        try:
            left_fixed = self.get_fixed(left)
            is_left_fixed = True
        except KeyError:
            is_left_fixed = False

        try:
            right_fixed = self.get_fixed(right)
            is_right_fixed = True
        except KeyError:
            is_right_fixed = False

        if is_left_fixed and is_right_fixed:
            raise UnificationError(
                f"{left} cannot equal {right} because {left_fixed} != {right_fixed}"
            )

        left_free, right_free = self.get_free(left), self.get_free(right)
        out_free, out_fixed = deepcopy(self.free), deepcopy(self.fixed)

        if left_free and right_free:
            out_free.remove(left_free)
            if right_free != left_free:
                out_free.remove(right_free)
            out_free.append(left_free | right_free)

        elif is_left_fixed:
            if right_free:
                out_free.remove(right_free)
                out_fixed[left_fixed].update(right_free)
            else:
                out_fixed[left_fixed].add(right)

        elif left_free:
            if is_right_fixed:
                out_free.remove(left_free)
                out_fixed[right_fixed].update(left_free)
            else:
                out_free.remove(left_free)
                out_free.append(left_free | {right})

        else:
            if is_right_fixed:
                out_fixed[right_fixed].add(left)
            elif right_free:
                out_free.remove(right_free)
                out_free.append(right_free | {left})
            else:
                out_free.append({left, right})
        return Equality(out_free, out_fixed)

    def add(self, left: Any, right: Any) -> Equality:
        if isinstance(left, Variable) and isinstance(right, Variable):
            return self._add_variable(left, right)
        if isinstance(right, Variable):
            return self._add_constant(right, left)
        if isinstance(left, Variable):
            return self._add_constant(left, right)
        if left == right:
            return self
        raise UnificationError(f"values dont match: {left} != {right}")

    def inject(self, term: Any, to_solve_for: Optional[Set[Variable]] = None) -> Set:
        term = construct(term)
        to_solve_for = to_solve_for or set()

        def _inject(_term):
            if isinstance(_term, ImmutableDict):
                return {
                    ImmutableDict(dict(zip(_term.keys(), v)))
                    for v in product(*map(_inject, _term.values()))
                }
            if isinstance(_term, PrologList):
                return {
                    PrologList(x, y)
                    for x, y in product(_inject(_term.head), _inject(_term.tail))
                }

            if isinstance(_term, Assign):
                if free := self.get_free(_term.variable) - {_term.variable}:
                    args_set = list(free)
                else:
                    args_set = [_term.variable]
                return [
                    Assign(a, _term.expression, _term.frame, is_injected=True)
                    for a in args_set
                ]

            if isinstance(_term, Variable):
                try:
                    return {self.get_fixed(_term)}
                except KeyError:
                    free = self.get_free(_term) & to_solve_for
                    if free:
                        return free
            return {_term}

        return _inject(term)

    def solutions(self, to_solve_for: Set[Variable]) -> Dict[Variable, Any]:
        out = {}
        for item in to_solve_for:
            try:
                fixed = self.get_fixed(item)
                deep = self.get_deep(fixed)
                out[item] = deconstruct(deep)
            except KeyError:
                pass
        return out

    def evaluate(self, assign_assert: Union[Assign, Assert]) -> Equality:
        value = assign_assert.expression(*map(self.get_fixed, assign_assert.variables))

        if isinstance(assign_assert, Assign):
            return self._add_constant(assign_assert.variable, value)

        #        if isinstance(assign_assert, Assert):
        if not value:
            raise UnificationError(f"bool({value}) != True")
        return self
