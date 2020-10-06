from __future__ import annotations

from collections import UserDict
from typing import Any, Dict, List, Optional, Set, Union


class Variable:
    @classmethod
    def factory(cls, *names: str) -> List:
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
        return hash(self.name) ^ hash(self.frame)

    def __eq__(self, other):
        if not isinstance(other, Variable):
            raise TypeError(f"{other} must be a Variable")
        return hash(self) == hash(other)

    def new_frame(self, frame):
        return Variable(self.name, frame=frame, many=self.many)

    @staticmethod
    def hash_set(variables: Set[Variable]) -> int:
        return hash(tuple(sorted(variables, key=lambda v: v.name)))

    def __iter__(self):
        yield Variable(self.name, frame=self.frame, many=True)


class ImmutableDict(UserDict):
    """https://www.python.org/dev/peps/pep-0351/
    """

    @staticmethod
    def construct(obj: Any):
        if isinstance(obj, dict):
            return ImmutableDict(
                {key: ImmutableDict.construct(value) for key, value in obj.items()}
            )
        if isinstance(obj, (list, tuple)):
            return tuple(map(ImmutableDict.construct, obj))
        if isinstance(obj, (bool, int, float, str, Variable, ImmutableDict)):
            return obj
        if obj is None:
            return obj
        raise TypeError(f"{obj} is not json serializable")

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

        self.data = {
            key: ImmutableDict.construct(value) for key, value in self.data.items()
        }

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
            if isinstance(obj, tuple):
                for value in obj:
                    _get_variables(value)
            if isinstance(obj, Variable):
                _variables.add(obj)

        _get_variables(self)
        return _variables


class UnificationError(ValueError):
    pass


class Rule:
    @staticmethod
    def negotiate_arg_types(obj):
        if isinstance(obj, dict):
            return ImmutableDict(obj)
        if not isinstance(obj, (ImmutableDict, Assign)):
            raise TypeError(f"{obj} must be an ImmutableDict")
        return obj

    def __init__(
        self, predicate: Union[ImmutableDict, Dict], *body: Union[ImmutableDict, Dict]
    ) -> None:

        self.predicate = Rule.negotiate_arg_types(predicate)
        self.body = tuple(map(Rule.negotiate_arg_types, body))

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
