"""parameter-names

Parameters should be named in snake_case with an optional _ to indicate unused parameters.
Signal parameters should be named in snake_case.
"""
from typing import cast

from lark import Token
import regex

from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex, positions_from_element, ParseTree
from codexgd.rules.common import SNAKE_CASE


rule.doc(__doc__, {"regex": None})


@rule.check(GDScriptCodex.parse_tree("func_arg_regular"))
@rule.check(GDScriptCodex.parse_tree("func_arg_inf"))
@rule.check(GDScriptCodex.parse_tree("func_arg_typed"))
@rule.check(GDScriptCodex.parse_tree("property_custom_setter"))
def func_arg(tree: ParseTree, options: Options):
    name = cast(Token, tree.children[0])
    if not options["regex"]:
        pattern = rf"^_?{SNAKE_CASE}$"
    else:
        pattern = str(options["regex"])

    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The parameter name '{name}' is not formated correctly.",
        )


@rule.check(GDScriptCodex.parse_tree("signal_arg_regular"))
@rule.check(GDScriptCodex.parse_tree("signal_arg_typed"))
def signal_arg(tree: ParseTree, options: Options):
    name = cast(Token, tree.children[0])
    if not options["regex"]:
        pattern = rf"^{SNAKE_CASE}$"
    else:
        pattern = str(options["regex"])

    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The parameter name '{name}' is not formated correctly.",
        )
