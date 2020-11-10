from __future__ import annotations

from copy import deepcopy
from itertools import product
from typing import Any, Dict, List, Optional, Sequence, Set

from multipledispatch import dispatch

from inference_logic.data_structures import (
    Assert,
    Assign,
    ImmutableDict,
    PrologList,
    PrologListNull,
    UnificationError,
    Variable,
    construct,
    deconstruct,
)


class Equality:
    """There are two types of equality:

    1. free, a Variable `X` can be equal to any number of other Variables
    2. fixed, a hashable object `h` can be equal to any number of Variables \
    so long as none of them are equal to any other hashable object.
    """

    def __init__(
        self,
        free: Sequence[Set[Variable]] = None,
        fixed: Dict[Any, Set[Variable]] = None,
    ) -> None:
        """the free and fixed components of and Equality can be passed as
        a List of Variable-Sets and a Dict of Variable-Sets respectively.

        >>> A, B, C, D, E = Variable.factory("A", "B", "C", "D", "E")
        >>> Equality(free=[{A, B}], fixed={True: {C, D}, False: {E}})
        {A, B}, True: {C, D}, False: {E}
        """
        self.fixed: Dict[ImmutableDict, Set[Variable]] = {}
        for constant, variable_set in (fixed or {}).items():
            self.fixed[constant] = variable_set.copy()
        self.free: List[Set[Variable]] = [
            variable_set.copy() for variable_set in free or []
        ]

    def __repr__(self) -> str:
        def variable_set_repr(variable_set):
            return f'{{{", ".join(sorted(map(str, variable_set)))}}}'

        fixed = [f"{k}: {variable_set_repr(v)}" for k, v in self.fixed.items()]
        free = list(map(variable_set_repr, self.free))
        return ", ".join(free + fixed) or "."

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

    def _get_free(self, variable: Variable) -> Set[Variable]:
        if not isinstance(variable, Variable):
            raise TypeError(f"{variable} must be a Variable")
        for variables in self.free:
            if variable in variables:
                return variables
        return set()

    def _get_fixed(self, variable: Variable) -> Any:
        if not isinstance(variable, Variable):
            raise TypeError(f"{variable} must be a Variable")
        for _variable in self._get_free(variable) | {variable}:
            for constant, variables in self.fixed.items():
                if _variable in variables:
                    return constant

        raise KeyError

    @dispatch(Variable)
    def get_deep(self, item):
        return self.get_deep(self._get_fixed(item))

    @dispatch(ImmutableDict)  # type: ignore
    def get_deep(self, item):
        return ImmutableDict({key: self.get_deep(value) for key, value in item.items()})

    @dispatch(PrologList)  # type: ignore
    def get_deep(self, item):
        try:
            return PrologList(self.get_deep(item.head), self.get_deep(item.tail))
        except RecursionError:
            raise

    @dispatch(object)  # type: ignore
    def get_deep(self, item):
        return item

    @dispatch(Variable, object)  # type: ignore
    def add(self, variable: Variable, constant: Any) -> Equality:
        try:
            hash(constant)
        except TypeError:
            raise TypeError(f"{constant} must be hashable")

        variable.many = False

        try:
            fixed = self._get_fixed(variable)

            if constant != fixed:
                raise UnificationError(
                    f"{variable} cannot equal {constant} because {constant} != {fixed}"
                )
            return self
        except KeyError:
            pass

        free = self._get_free(variable)
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

    @dispatch(Variable, Variable)  # type: ignore
    def add(self, left: Variable, right: Variable) -> Equality:

        try:
            left_fixed = self._get_fixed(left)
            is_left_fixed = True
        except KeyError:
            is_left_fixed = False

        try:
            right_fixed = self._get_fixed(right)
            is_right_fixed = True
        except KeyError:
            is_right_fixed = False

        if is_left_fixed and is_right_fixed:
            raise UnificationError(
                f"{left} cannot equal {right} because {left_fixed} != {right_fixed}"
            )

        left_free, right_free = self._get_free(left), self._get_free(right)
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

    @dispatch(object, Variable)  # type: ignore
    def add(self, left: Any, right: Any) -> Equality:
        return self.add(right, left)

    @dispatch(object, object)  # type: ignore
    def add(self, left: Any, right: Any) -> Equality:
        if left == right:
            return self
        raise UnificationError(f"values dont match: {left} != {right}")

    @dispatch(ImmutableDict, to_solve_for=set)  # type: ignore
    def inject(self, term: Any, to_solve_for: Set[Variable]) -> Set:
        term = construct(term)
        to_solve_for = to_solve_for or set()

        return {
            ImmutableDict(dict(zip(term.keys(), v)))
            for v in product(
                *[self.inject(x, to_solve_for=to_solve_for) for x in term.values()]
            )
        }

    @dispatch(PrologList, to_solve_for=set)  # type: ignore
    def inject(self, term: Any, to_solve_for: Optional[Set[Variable]] = None) -> Set:
        return {
            PrologList(x, y)
            for x, y in product(
                self.inject(term.head, to_solve_for=to_solve_for),
                self.inject(term.tail, to_solve_for=to_solve_for),
            )
        }

    @dispatch(Assign, to_solve_for=set)  # type: ignore
    def inject(self, term: Any, to_solve_for: Set[Variable]) -> List:
        free = self._get_free(term.variable) - {term.variable}
        if free:
            args_set = list(free)
        else:
            args_set = [term.variable]
        return {
            Assign(a, term.expression, term.frame, is_injected=True) for a in args_set
        }

    @dispatch(Variable, to_solve_for=set)  # type: ignore
    def inject(self, term: Any, to_solve_for: Set[Variable]) -> Set:
        try:
            return {self._get_fixed(term)}
        except KeyError:
            free = self._get_free(term) & to_solve_for
            if free:
                return free
            return {term}

    @dispatch(object, to_solve_for=set)  # type: ignore
    def inject(self, term: Any, to_solve_for: Set[Variable]) -> Set:
        return {term}

    def solutions(self, to_solve_for: Set[Variable]) -> Dict[Variable, Any]:
        out = {}
        for item in to_solve_for:
            try:
                fixed = self._get_fixed(item)
                deep = self.get_deep(fixed)
                out[item] = deconstruct(deep)
            except KeyError:
                pass
        return out

    @dispatch(Assign)  # type: ignore
    def evaluate(self, assignment: Assign) -> Equality:
        value = assignment.expression(*map(self._get_fixed, assignment.variables))
        return self.add(assignment.variable, value)

    @dispatch(Assert)  # type: ignore
    def evaluate(self, assertion: Assert) -> Equality:
        value = assertion.expression(*map(self._get_fixed, assertion.variables))
        if not value:
            raise UnificationError(f"bool({value}) != True")
        return self

    @dispatch(ImmutableDict, ImmutableDict)  # type: ignore
    def unify(self, left, right) -> Equality:
        if left.keys() != right.keys():
            raise UnificationError(f"keys must match: {tuple(left)} != {tuple(right)}")

        equality = self
        for key in left.keys():
            equality = equality.unify(left[key], right[key])
        return equality

    @dispatch(PrologList, PrologList)  # type: ignore
    def unify(self, left, right) -> Equality:
        return self.unify(left.head, right.head).unify(left.tail, right.tail)

    @dispatch(PrologList, PrologListNull)  # type: ignore
    def unify(self, left, right) -> Equality:
        raise UnificationError("list lengths must be the same")

    @dispatch(PrologListNull, PrologList)  # type: ignore
    def unify(self, left, right) -> Equality:
        raise UnificationError("list lengths must be the same")

    @dispatch(object, object)  # type: ignore
    def unify(self, left, right) -> Equality:
        """
        Unification is a key idea in declarative programming.
        https://en.wikipedia.org/wiki/Unification_(computer_science)

        This function has 3 tasks:

        1. Unification of values:

            >>> A, B, C = Variable.factory("A", "B", "C")

            When two primitive values are unified it will check that they are
            equal to each other, and return an empty Equality object.

            >>> Equality().unify(1, 1)
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

        return self.add(left, right)
