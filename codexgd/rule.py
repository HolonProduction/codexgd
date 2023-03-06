from typing import Dict, Callable, Iterable, Union, List, cast, Tuple, Optional

from enum import Enum, unique

import inspect
import os

from typing_extensions import (
    TypeVarTuple,
    Protocol,
    Any,
    Unpack,
)

from .problem import Problem
from .exceptions import CodexGDError
from .callback import Callback


class RuleRegistrationError(CodexGDError):
    """Errors that happen while a rule is loaded."""


@unique
class Severity(Enum):
    """The way a certain rule is treated when reporting problems."""

    OFF = "off"
    WARN = "warn"
    ERROR = "error"


Options = Dict[str, Union[str, int, float, bool, None]]

Parameter = TypeVarTuple("Parameter")
Bindings = TypeVarTuple("Bindings")


class CallbackDict(Protocol):
    """Protocoll for a dictionary with entries that use generics."""

    def __getitem__(
        self, item: Callback[Unpack[Parameter]]
    ) -> List[Callable[[Unpack[Parameter], Options], Iterable[Problem]]]:
        ...

    def __setitem__(
        self,
        item: Callback[Unpack[Parameter]],
        value: List[Callable[[Unpack[Parameter], Options], Iterable[Problem]]],
    ):
        ...

    def values(
        self,
    ) -> List[Callable[[Unpack[Tuple[Any, ...]], Options], Iterable[Problem]]]:
        ...

    def __contains__(self, item: Any) -> bool:
        ...


class Rule:
    """Representation of a loaded rule."""

    name: str
    info: str
    severity: Severity
    options: Options
    callbacks: CallbackDict
    origin: str

    def __str__(self) -> str:
        return (
            'Rule("'
            + self.name
            + '", "'
            + self.info
            + '", '
            + str(self.severity)
            + ", "
            + str(self.options)
            + ")"
        )

    def __init__(self):
        self.severity = Severity.OFF
        self.callbacks = cast(CallbackDict, {})
        self.origin = ""

    def __call__(self, name: str, info: str, options: Optional[Options] = None) -> None:
        if options is None:
            options = {}

        if "name" in self.__dict__ or "info" in self.__dict__:
            raise RuleRegistrationError("You may only define one rule per module.")

        self.name = name
        self.info = info
        self.options = options

        self.origin = os.path.normpath(os.path.realpath(inspect.stack()[1][1]))

    def doc(self, docstring: str, options: Optional[Options] = None) -> None:
        """Utility function that extracts name and info from a docstring."""
        if options is None:
            options = {}

        lines = list(filter(lambda x: x != "", docstring.splitlines()))
        name = lines[0].strip()
        info = lines[1].strip()

        self(name, info, options)
        # Correct the origin because __call__ is now called from this file.
        self.origin = os.path.normpath(os.path.realpath(inspect.stack()[1][1]))

    def check(
        self, callback: Callback[Unpack[Parameter]], *bindings: Unpack[Bindings]
    ) -> Callable[
        [
            # pylint: disable-next=line-too-long
            Callable[[Unpack[Parameter], Options, Unpack[Bindings]], Iterable[Problem]]  # type: ignore
        ],
        Callable[[Unpack[Parameter], Options, Unpack[Bindings]], Iterable[Problem]],  # type: ignore
    ]:
        def decorator(
            callable_to_connect: Callable[
                [Unpack[Parameter], Options, Unpack[Bindings]], Iterable[Problem]  # type: ignore
            ]
        ) -> Callable[
            [Unpack[Parameter], Options, Unpack[Bindings]], Iterable[Problem]  # type: ignore
        ]:
            def bind(
                *parameters: Unpack[Tuple[Unpack[Parameter], Options]]
            ) -> Iterable[Problem]:
                yield from callable_to_connect(*parameters, *bindings)

            if callback not in self.callbacks:
                self.callbacks[callback] = []
            if callable_to_connect not in self.callbacks[callback]:
                self.callbacks[callback].append(bind)
            return callable_to_connect

        return decorator


rule: Rule
