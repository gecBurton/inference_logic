from __future__ import annotations

from collections import UserDict
from typing import Any, Dict, List, Optional, Set, Union


def new_frame(obj, frame: int):
    if isinstance(obj, (Variable, ImmutableDict, PrologList)):
        return obj.new_frame(frame)
    return obj


class Variable:
    @classmethod
    def factory(cls, *names: str) -> List:
        """
        helper method to generate many Variables

        :examples:
            >>> Variable.factory("A", "B", "C")
            [A, B, C]
        """
        return list(map(cls, names))

    def __init__(
        self, name: str, frame: Optional[int] = None, many: bool = False
    ) -> None:
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if name[0].islower():
            raise ValueError("name must begin with a uppercase letter")
        self.name = name
        self.frame = frame
        self.many = many

    def __repr__(self) -> str:
        many = "*" if self.many else ""
        frame = f"_{self.frame}" if self.frame is not None else ""
        return f"{many}{self.name}{frame}"

    def __hash__(self):
        return hash((self.name, self.frame))

    def __eq__(self, other):
        """
        :examples:
            >>> A, B = Variable.factory("A", "B")

            >>> A == Variable("A")
            True

            >>> A == B
            False
        """
        if not isinstance(other, Variable):
            raise TypeError(f"{other} must be a Variable")
        return hash(self) == hash(other)

    def new_frame(self, frame):
        """
        :example:
            >>> A = Variable("A")
            >>> A.new_frame(1)
            A_1
        """
        return Variable(self.name, frame=frame, many=self.many)

    @staticmethod
    def hash_set(variables: Set[Variable]) -> int:
        return hash(tuple(sorted(variables, key=lambda v: v.name)))

    def __iter__(self):
        yield Variable(self.name, frame=self.frame, many=True)


class PrologListNull:
    def __repr__(self):
        return ".()"

    def __hash__(self):
        return hash("hello!")

    def __eq__(self, other):
        if not isinstance(other, PrologListNull):
            raise TypeError(f"{other} must be a PrologListNull")
        return True


def construct(obj: Any):
    if isinstance(obj, dict):
        return ImmutableDict({key: construct(value) for key, value in obj.items()})
    if isinstance(obj, (list, tuple)):
        if not obj:
            return PrologListNull()

        head, *tail = reversed(list(map(construct, obj)))
        out = (
            head
            if obj and isinstance(head, Variable) and head.many
            else PrologList(head, PrologListNull())
        )

        for item in tail:
            out = PrologList(item, out)
        return out

    if isinstance(
        obj,
        (
            bool,
            int,
            float,
            str,
            Variable,
            ImmutableDict,
            PrologList,
            Rule,
            Assert,
            Assign,
            PrologListNull,
        ),
    ):
        return obj
    if obj is None:
        return obj
    raise TypeError(f"{obj} is not json serializable")


def deconstruct(obj):
    if isinstance(obj, ImmutableDict):
        return {key: deconstruct(value) for key, value in obj.items()}
    if isinstance(obj, PrologList):
        if isinstance(obj.tail, PrologListNull):
            return [deconstruct(obj.head)]
        return [deconstruct(obj.head), *deconstruct(obj.tail)]
    return obj


class PrologList:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __hash__(self):
        return hash((self.head, self.tail))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f".({self.head}, {self.tail})"

    def new_frame(self, frame: int) -> PrologList:
        return PrologList(new_frame(self.head, frame), new_frame(self.tail, frame))


class ImmutableDict(UserDict):
    """https://www.python.org/dev/peps/pep-0351/
    """

    def _immutable(self, *args, **kws):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable  # type: ignore
    setdefault = _immutable
    pop = _immutable  # type: ignore
    popitem = _immutable

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("expected at most 1 arguments, got %d" % len(args))
        if args:
            self.data = args[0]
        elif "dict" in kwargs:
            self.data = kwargs.pop("dict")
            import warnings

            warnings.warn(
                "Passing 'dict' as keyword argument is deprecated",
                DeprecationWarning,
                stacklevel=2,
            )
        else:
            self.data = {}

        if kwargs:
            self.data.update(kwargs)

        for key in self.data:
            if not isinstance(key, str):
                raise TypeError(f"{key} must be a string")

        self.data = {key: construct(value) for key, value in self.data.items()}

    def keys(self):
        return self.data.keys()

    def __hash__(self) -> int:
        return hash(tuple(self.items()))

    def __eq__(self, other):
        if not isinstance(other, ImmutableDict):
            raise TypeError(f"{other} must be an ImmutableDict")
        return hash(self) == hash(other)

    def get_variables(self) -> Set[Variable]:
        _variables = set()

        def _get_variables(obj):
            if isinstance(obj, ImmutableDict):
                for value in obj.values():
                    _get_variables(value)
            if isinstance(obj, PrologList):
                _get_variables(obj.head)
                _get_variables(obj.tail)
            if isinstance(obj, Variable):
                _variables.add(obj)

        _get_variables(self)
        return _variables

    def new_frame(self, frame: int) -> ImmutableDict:
        return ImmutableDict({k: new_frame(v, frame) for k, v in self.items()})


class UnificationError(ValueError):
    pass


class Rule:
    def __init__(
        self, predicate: Union[ImmutableDict, Dict], *body: Union[ImmutableDict, Dict]
    ) -> None:

        self.predicate = construct(predicate)
        self.body = tuple(map(construct, body))

    def __eq__(self, other):
        if not isinstance(other, Rule):
            raise TypeError(f"{other} must be a Rule")
        return self.predicate == other.predicate and self.body == other.body

    def __repr__(self) -> str:
        if self.body:
            body_repr = " ∧ ".join(map(repr, self.body))
            return f"{self.predicate} ¬ {body_repr}."
        else:
            return f"{self.predicate}."

    def new_frame(self, frame: int) -> Rule:
        return Rule(
            self.predicate.new_frame(frame), *(o.new_frame(frame) for o in self.body),
        )


class Assign:
    def __init__(self, variable: Variable, expression, frame=None, is_injected=False):
        self.variable = variable
        self.expression = expression
        self.frame = frame
        self.variables = Variable.factory(*self.expression.__code__.co_varnames)
        if self.frame is not None:
            if not is_injected:
                self.variable = self.variable.new_frame(self.frame)
            self.variables = [
                variable.new_frame(self.frame) for variable in self.variables
            ]

    def new_frame(self, frame: int) -> Assign:
        return Assign(self.variable, self.expression, frame)


class Assert:
    def __init__(self, expression, frame=None):
        self.expression = expression
        self.frame = frame
        self.variables = [Variable(arg) for arg in self.expression.__code__.co_varnames]
        if self.frame is not None:
            self.variables = [
                variable.new_frame(self.frame) for variable in self.variables
            ]

    def new_frame(self, frame: int) -> Assert:
        return Assert(self.expression, frame)
