"""quotes

TODO: Write docs.
"""

from typing import Iterable, cast, ClassVar

from lark import Token

from codexgd.rule import rule, Options, Problem
from codexgd.gdscript import GDScriptCodex, ParseTree, positions_from_element
from codexgd.rules.common import extract_string


rule.doc(__doc__)


@rule.check(GDScriptCodex.parse_tree("string"))
def quotes(tree: ParseTree, _options: Options):
    string = cast(Token, tree.children[0])
    is_multiline = string.type == "LONG_STRING"

    if tree.meta.line == tree.meta.end_line and is_multiline:
        yield Problem(
            *positions_from_element(tree),
            rule,
            "Do not use multiline strings if not needed.",
        )

    content = cast(str, extract_string(string))
    if is_multiline:

        class Quotes:
            amount: int
            char: str
            last: bool
            _single_count: ClassVar[int] = 0
            _double_count: ClassVar[int] = 0

            def __init__(self, char: str, amount: int, last: bool = False) -> None:
                self.char = char
                self.amount = amount
                self.last = last
                self._count()

            def _count(self):
                needs_escape = int(self.amount / 3)
                if self.last and self.amount % 3 != 0:
                    needs_escape += 1

                if self.char == "'":
                    self.__class__._single_count += needs_escape
                else:
                    self.__class__._double_count += needs_escape

            def needs_escape(self) -> bool:
                return (
                    self.__class__._single_count < self.__class__._double_count
                ) == (self.char == "'")

            def get_optimal(self) -> str:
                res = ""
                for i in range(1, self.amount + 1):
                    if (
                        i % 3 == 0 or (i == self.amount and self.last)
                    ) and self.needs_escape():
                        res += "\\" + self.char
                    else:
                        res += self.char
                return res

        structure = []
        structure.append("")

        escaping = False
        strike = 0
        last = ""
        for char in content:
            if char == "\\":
                if escaping:
                    last = "\\"
                    strike = 0
                escaping = not escaping
            elif char == "'":
                strike += 1
                escaping = False
                last = char
            elif char == '"':
                strike += 1
                escaping = False
                last = char
            else:
                if strike > 0:
                    structure.append(Quotes(last, strike))

                strike = 0
                if isinstance(structure[-1], str):
                    structure[-1] += char
                else:
                    structure.append(char)
                last = char

        if strike > 0:
            structure.append(Quotes(last, strike, True))

        escape_single = Quotes._single_count < Quotes._double_count
        optimal = ""
        for i in structure:
            if isinstance(i, str):
                optimal += i
            else:
                optimal += i.get_optimal()
    else:
        escape_single = content.count("'") < content.count('"')

        optimal = ""
        escaping = False
        for char in content:
            if char == "\\":
                if escaping:
                    optimal += "\\\\"
                escaping = not escaping
            elif char == "'":
                if escape_single:
                    optimal += "\\'"
                else:
                    optimal += "'"
                escaping = False
            elif char == '"':
                if escape_single:
                    optimal += '"'
                else:
                    optimal += '\\"'
                escaping = False
            else:
                if escaping:
                    escaping = False
                    optimal += "\\"
                optimal += char

    quote = ("'" if escape_single else '"') * (3 if is_multiline else 1)

    optimal = quote + optimal + quote

    if optimal != string:
        yield Problem(
            *positions_from_element(tree),
            rule,
            f"There is a better way to handle quotes: {optimal}",
        )
