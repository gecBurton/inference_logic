from __future__ import annotations

from collections import UserDict
from typing import Any, Dict, List, Optional, Set, Union

from multipledispatch import dispatch


class Variable:
    @classmethod
    def factory(cls, *names: str) -> List[Variable]:
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
        self.name = name
        self.frame = frame
        self.many = many

    def __repr__(self) -> str:
        many = "*" if self.many else ""
        frame = f":{self.frame}" if self.frame is not None else ""
        return f"{many}{self.name}{frame}"

    def __hash__(self) -> int:
        return hash((self.name, self.frame))

    def __eq__(self, other) -> bool:
        """
        :examples:
            >>> A, B = Variable.factory("A", "B")

            >>> A == Variable("A")
            True

            >>> A == B
            False

            >>> A == 1
            Traceback (most recent call last):
                ...
            TypeError: 1 must be a Variable
        """
        if not isinstance(other, Variable):
            raise TypeError(f"{other} must be a Variable")
        return hash(self) == hash(other)

    @staticmethod
    def hash_set(variables: Set[Variable]) -> int:
        return hash(tuple(sorted(variables, key=lambda v: v.name)))

    def __iter__(self):
        yield Variable(self.name, frame=self.frame, many=True)


class PrologListNull:
    """This is an Object that signifies the end of a PrologList
    """

    def __len__(self):
        return 0

    def __hash__(self) -> int:
        return hash("hello!")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PrologListNull):
            raise UnificationError(f"{other} must be a PrologListNull")
        return True

    def __iter__(self):
        yield from iter([])


class PrologList:
    """A list in Prolog is build recursively out of the first, head, element
    and everything else, the tail.
    """

    def __len__(self):
        return 1 + len(self.tail)

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __hash__(self) -> int:
        return hash((self.head, self.tail))

    def __eq__(self, other) -> bool:
        if not isinstance(other, PrologList):
            raise UnificationError(f"{other} must be a PrologList")
        return hash(self) == hash(other)

    def __repr__(self) -> str:
        if isinstance(self.tail, PrologListNull):
            return f"[{self.head}]"
        return f"[{self.head}, {repr(self.tail)[1:-1]}]"

    def __add__(self, other):
        if not isinstance(other, PrologList):
            raise UnificationError(f"{other} must be a PrologList")

        # TODO: this is hideous!
        a, b = deconstruct(self), deconstruct(other)
        c = a + b
        return construct(c)

    def __iter__(self):
        yield self.head
        yield from iter(self.tail)


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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ImmutableDict):
            raise TypeError(f"{other} must be an ImmutableDict")
        return hash(self) == hash(other)


def get_variables(immutable_dict: ImmutableDict) -> Set[Variable]:
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

    _get_variables(immutable_dict)
    return _variables


class UnificationError(ValueError):
    pass


class Rule:
    def __init__(
        self,
        predicate: Union[ImmutableDict, Dict],
        *body: Union[ImmutableDict, Dict, Assert],
    ) -> None:

        self.predicate = construct(predicate)
        self.body = tuple(map(construct, body))

    def __eq__(self, other: Any) -> bool:
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
                self.variable = new_frame(self.variable, self.frame)
            self.variables = [
                new_frame(variable, self.frame) for variable in self.variables
            ]


class Assert:
    def __init__(self, expression, frame=None):
        self.expression = expression
        self.frame = frame
        self.variables = [Variable(arg) for arg in self.expression.__code__.co_varnames]
        if self.frame is not None:
            self.variables = [
                new_frame(variable, self.frame) for variable in self.variables
            ]


@dispatch(ImmutableDict)
def deconstruct(obj):
    return {key: deconstruct(value) for key, value in obj.items()}


@dispatch(PrologList)  # type: ignore
def deconstruct(obj):
    if isinstance(obj.tail, PrologListNull):
        return [deconstruct(obj.head)]
    if isinstance(obj.head, PrologListNull):
        return []

    return [deconstruct(obj.head), *deconstruct(obj.tail)]


@dispatch(object)  # type: ignore
def deconstruct(obj):
    return obj


@dispatch(dict)
def construct(obj: Any):
    return ImmutableDict({key: construct(value) for key, value in obj.items()})


@dispatch((list, tuple))  # type: ignore
def construct(obj: Any):
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


@dispatch(  # type: ignore
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
    )
)
def construct(obj: Any):
    return obj


@dispatch(object)  # type: ignore
def construct(obj: Any):
    if obj is None:
        return obj
    raise TypeError(f"{obj} is not json serializable")


@dispatch(Rule, int)  # type: ignore
def new_frame(obj, frame: int):
    return Rule(
        new_frame(obj.predicate, frame), *(new_frame(o, frame) for o in obj.body),
    )


@dispatch(Assign, int)  # type: ignore
def new_frame(obj, frame: int):
    return Assign(obj.variable, obj.expression, frame)


@dispatch(Assert, int)  # type: ignore
def new_frame(obj, frame: int):
    return Assert(obj.expression, frame)


@dispatch(ImmutableDict, int)  # type: ignore
def new_frame(obj, frame: int):
    return ImmutableDict({k: new_frame(v, frame) for k, v in obj.items()})


@dispatch(Variable, int)  # type: ignore
def new_frame(obj, frame: int):
    """
    :example:
        >>> A = Variable("A")
        >>> new_frame(A, 1)
        A:1
    """
    return Variable(obj.name, frame=frame, many=obj.many)


@dispatch(PrologList, int)  # type: ignore
def new_frame(obj, frame: int):
    return PrologList(new_frame(obj.head, frame), new_frame(obj.tail, frame))


@dispatch(object, int)  # type: ignore
def new_frame(obj, frame: int):
    return obj
