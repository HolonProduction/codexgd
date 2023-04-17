"""variable-names

Variables should be named in snake_case which may have a prefix to indicate private variables.
Constant should be named in CONSTANT_CASE which may have a prefix to indicate private constants. 
When preloading classes into constants or variables they should be named in PascalCase.
"""
from typing import cast, Tuple

from lark import Token
import regex

from codexgd.rule import rule, Options, Problem
from codexgd.gdscript import GDScriptCodex, ParseTree, positions_from_element
from codexgd.rules.common import SNAKE_CASE, PASCAL_CASE, CONSTANT_CASE, is_type


rule.doc(
    __doc__,
    {
        "private-prefix": "_",
        "variable-regex": None,
        "constant-regex": None,
        "type-regex": None,
    },
)


@rule.check(GDScriptCodex.parse_tree("func_var_empty"), -1)
@rule.check(GDScriptCodex.parse_tree("class_var_empty"), -1)
@rule.check(GDScriptCodex.parse_tree("func_var_assigned"), 1)
@rule.check(GDScriptCodex.parse_tree("class_var_assigned"), 1)
@rule.check(GDScriptCodex.parse_tree("func_var_typed"), -1)
@rule.check(GDScriptCodex.parse_tree("class_var_typed"), -1)
@rule.check(GDScriptCodex.parse_tree("func_var_typed_assgnd"), 2)
@rule.check(
    GDScriptCodex.parse_tree("class_var_typed_assgnd"),
    2,
)  # typo in gdparse
@rule.check(GDScriptCodex.parse_tree("func_var_inf"), 1)
@rule.check(GDScriptCodex.parse_tree("class_var_inf"), 1)
def variables(
    tree: ParseTree,
    options: Options,
    value_index: int,
):
    name = cast(Token, tree.children[0])

    if value_index >= 0 and is_type(tree.children[value_index]):
        if not options["type-regex"]:
            pattern = rf"^({options['private-prefix']})?{PASCAL_CASE}$"
        else:
            pattern = str(options["type-regex"])
    else:
        if not options["variable-regex"]:
            pattern = rf"^({options['private-prefix']})?{SNAKE_CASE}$"
        else:
            pattern = str(options["variable-regex"])

    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The variable name '{name}' is not formated correctly.",
        )


@rule.check(GDScriptCodex.parse_tree("const_assigned"), 1)
@rule.check(GDScriptCodex.parse_tree("const_inf"), 1)
@rule.check(GDScriptCodex.parse_tree("const_typed_assigned"), 2)
def constants(tree: ParseTree, options: Options, value_index: int):
    name = cast(Token, tree.children[0])

    if is_type(tree.children[value_index]):
        if not options["type-regex"]:
            pattern = rf"^({options['private-prefix']})?{PASCAL_CASE}$"
        else:
            pattern = str(options["type-regex"])
    else:
        if not options["constant-regex"]:
            pattern = rf"^({options['private-prefix']})?{CONSTANT_CASE}$"
        else:
            pattern = str(options["constant-regex"])

    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            f"The constant name '{name}' is not formated correctly.",
        )
