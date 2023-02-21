from typing import Tuple, Union, overload, cast
from lark import Token, ParseTree
from ..problem import Position


COMPLETE_FILE = ((-1, -1), (-1, -1))


@overload
def positions_from_element(element: Token) -> Tuple[Position, Position]:
    ...


@overload
def positions_from_element(element: ParseTree) -> Tuple[Position, Position]:
    ...


def positions_from_element(
    element: Union[Token, ParseTree]
) -> Tuple[Position, Position]:
    if isinstance(element, Token):
        return cast(
            Tuple[Position, Position],
            ((element.line, element.column), (element.end_line, element.end_column)),
        )
    return (element.meta.line, element.meta.column), (
        element.meta.end_line,
        element.meta.end_column,
    )
