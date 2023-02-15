from typing import Generic
from typing_extensions import TypeVar, TypeVarTuple, Self, Type, Unpack

Values = TypeVarTuple("Values")


class Callback(Generic[Unpack[Values]]):
    """A callback allows the rules to hook into some processing step of the codex."""


Identifier = TypeVar("Identifier")


class DynamicCallback(Callback[Unpack[Values]], Generic[Unpack[Values], Identifier]):
    """
    A dynamic callback allows to pass an identifier.
    This allows the codex to notify only certain group of listeners.
    """

    _identifier: Identifier

    def __init__(self, identifier: Identifier) -> None:
        self._identifier = identifier

    def __eq__(self, other: "DynamicCallback") -> bool:
        return self._identifier == other._identifier

    def __hash__(self) -> int:
        return hash((self.__class__, self._identifier))

    @classmethod
    def factory(cls: Type[Self], identifier: Identifier) -> Self:
        return cls(identifier)
