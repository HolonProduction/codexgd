from typing import Tuple
from lark import Token
from ..problem import Position


COMPLETE_FILE = ((-1, -1), (-1, -1))


def positions_from_token(token: Token) -> Tuple[Position, Position]:
    return (token.line, token.column), (token.end_line, token.end_column)
