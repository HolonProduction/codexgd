"""class-names

Class names should use PascalCase.
"""
from typing import cast

import regex

from lark import Token

from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, positions_from_element
from codexgd.rule import rule, Options
from codexgd.rules.common import PASCAL_CASE


rule.doc(__doc__, {"regex": None})


@rule.check(GDScriptCodex.parse_tree("classname_stmt"))
def parse_tree_element(tree: ParseTree, options: Options):
    if not options["regex"]:
        pattern = rf"^{PASCAL_CASE}$"
    else:
        pattern = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The class name '{name}' is not formated correctly.",
        )
