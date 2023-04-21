"""quotes

TODO: Write docs.
"""

from typing import Iterable, cast

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
        single = 0
        double = 0

        SINGLE = 0
        DOUBLE = 1
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
                escaping = False
                if last == "'":
                    strike += 1
                    if strike == 2:
                        strike = 0
                        last = ""
                        structure.append(SINGLE)
                        single += 1
                        continue

                last = "'"
            elif char == '"':
                escaping = False
                if last == '"':
                    strike += 1
                    if strike == 2:
                        strike = 0
                        last = ""
                        structure.append(DOUBLE)
                        double += 1
                        continue

                last = '"'
            else:
                strike = 0
                if isinstance(structure[-1], str):
                    structure[-1] += char
                else:
                    structure.append(char)
                last = char

        escape_single = single < double
        optimal = ""
        for i in structure:
            if isinstance(i, str):
                optimal += i
            elif i == SINGLE:
                optimal += "\\'\\'\\'" if escape_single else "'''"
            else:
                optimal += '"""' if escape_single else '\\"\\"\\"'
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
