from typing import TYPE_CHECKING, Tuple

from dataclasses import dataclass

if TYPE_CHECKING:
    from .rule import Rule


# line, column
Position = Tuple[int, int]


@dataclass
class Problem:
    """
    In start a -1 means the very first. So if line is -1 the problem starts in the first line.
    If the column is -1 it will start at the first char as well.
    In end a -1 means the very last so the problem would end in the last line or at the last char.
    """

    start: Position
    end: Position
    rule: "Rule"
    info: str
