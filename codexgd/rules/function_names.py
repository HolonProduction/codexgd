"""function-names

Function names should use snake case which may have a prefix to indicate private functions.

Good:
```gdscript
func _private_method()
func public_method()
func 2d_stuff()
```
Bad:
```gdscript
func PascalCase()
```

Options:
- `private-prefix = "_"`  
The prefix for private functions. Supports regex.
**Use the corresponding variable! (Except you know what you are doing.)**
- `connected-pascal-case = True`  
Whether to allow PascalCase for connected functions (`on_BodyEntered_kinematic_body`).
- `regex = None`  
Provide a custom regex for function names. When this is set all other options will be ignored.
"""
from typing import cast

import regex

from lark import Token

from codexgd.rule import rule, Options
from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, positions_from_element


rule.doc(__doc__, {"private-prefix": "_", "connected-pascal-case": True, "regex": None})


@rule.check(GDScriptCodex.parse_tree("func_header"))
def parse_tree_element(tree: ParseTree, options: Options):
    if not options["regex"]:
        pattern = (
            rf"^({options['private-prefix']}|_)?(%s[\p{{Ll}}1-9]+)(_[\p{{Ll}}1-9]+)*$"
            % (
                r"(on_[\p{Lu}][\p{Ll}\p{Lu}1-9]+)|"
                if options["connected-pascal-case"]
                else r"",
            )
        )
    else:
        pattern = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            "The function name '" + name + "' is not formated correctly.",
        )
