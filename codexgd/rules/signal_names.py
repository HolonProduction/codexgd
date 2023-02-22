"""signal-names

Signals should be named in snake_case.
"""
from typing import cast

import regex
from lark import Token

from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex, positions_from_element, ParseTree
from codexgd.rules.common import SNAKE_CASE


rule.doc(__doc__, {"regex": None})


@rule.check(GDScriptCodex.parse_tree("signal_stmt"))
def signal_stmt(tree: ParseTree, options: Options):
    name = cast(Token, tree.children[0])

    if options["regex"]:
        pattern = str(options["regex"])
    else:
        pattern = rf"^{SNAKE_CASE}$"

    match = regex.match(pattern, name)
    if not match:
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The signal name '{name}' is not formated correctly.",
        )
