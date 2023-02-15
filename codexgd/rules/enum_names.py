"""enum-names

Enums should be named in PascalCase which may have a prefix to indicate private enums.
"""
from typing import cast
import regex

from lark import Token

from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex, ParseTree, positions_from_token
from codexgd.rules.common import PASCAL_CASE


rule.doc(__doc__, {"private-prefix": "_", "regex": None})


@rule.check(GDScriptCodex.parse_tree("enum_named"))
def parse_tree_enum_named(tree: ParseTree, options: Options):
    if not options["regex"]:
        pattern = rf"^({options['private-prefix']})?{PASCAL_CASE}$"
    else:
        pattern = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_token(name),
            rule,
            f"The enum name '{name}' is not formated correctly.",
        )
