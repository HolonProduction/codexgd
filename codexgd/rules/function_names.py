"""function-names

Function names should use snake case which may have a prefix to indicate private functions.

Good:
```gdscript
func _private_method()
func public_method()
func 2d_stuff()
```
Bad:
```
func PascalCase()
```

Options:
**Use the corresponding variable! (Except you know what you are doing.)**
private-prefix = "_"            The prefix for private functions. Supports regex.

connected-pascal-case = True    Whether to allow PascalCase for connected functions. (`on_BodyEntered_kinematic_body`)
regex = None                    Provide a custom regex for function names. When this is set all other options will be ignored.
"""
from typing import Iterable, cast

import re

from lark import Token

from codexgd.rule import rule, Options
from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, positions_from_token


rule.doc(__doc__, {"private-prefix": "_", "connected-pascal-case": True, "regex": None})


@rule.check(GDScriptCodex.parse_tree("func_header"))
def parse_tree_element(tree: ParseTree, options: Options) -> Iterable[Problem]:
    if not options["regex"]:

        regex = r"^(%s|_)?(%s[a-z1-9]+)(_[a-z1-9]+)*$" % (
            options["private-prefix"],
            r"(on_[A-Z][a-zA-Z1-9]+)|" if options["connected-pascal-case"] else r"",
        )
    else:
        regex = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not re.match(regex, name):
        yield Problem(
            *positions_from_token(name),
            rule,
            "The function name '" + name + "' is not formated correctly."
        )
