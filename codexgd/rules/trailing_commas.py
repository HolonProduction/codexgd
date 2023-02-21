"""trailing-commas

Use trailing commas in arrays, dictionaries and enums.
"""
from lark import Tree

from codexgd.rule import rule, Options, Problem
from codexgd.gdscript import GDScriptCodex, ParseTree, positions_from_element


rule.doc(__doc__)


@rule.check(GDScriptCodex.parse_tree("array"))
@rule.check(GDScriptCodex.parse_tree("dict"))
@rule.check(GDScriptCodex.parse_tree("enum_body"))
def check(tree: ParseTree, _options: Options):
    has_trailing_comma = (
        len(tree.children) > 0
        and isinstance(tree.children[-1], Tree)
        and tree.children[-1].data == "trailing_comma"
    )
    if tree.meta.line == tree.meta.end_line:
        if has_trailing_comma:
            yield Problem(
                *positions_from_element(tree), rule, "No trailing comma is needed."
            )
    else:
        if not has_trailing_comma:
            yield Problem(
                *positions_from_element(tree), rule, "A trailing comma is needed."
            )
