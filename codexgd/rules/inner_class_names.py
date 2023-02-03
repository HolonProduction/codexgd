"""inner-class-names

Inner class names should use PascalCase which may have a prefix to indicate private classes.

Good:
```gdscript
class PascalCase
class _PrivateClass
```
Bad:
```
class snake_case
```

Options:
**Use the corresponding variable! (Except you know what you are doing.)**
private-prefix = "_"            The prefix for private classes. Supports regex.

regex = None                    Provide a custom regex for class names. When this is set all other options will be ignored.
"""
from typing import Iterable, cast

import re

from lark import Token

from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, positions_from_token
from codexgd.rule import rule, Options


rule.doc(__doc__, {"private-prefix": "_", "regex": None})


@rule.check(GDScriptCodex.parse_tree("class_def"))
def parse_tree_element(tree: ParseTree, options: Options) -> Iterable[Problem]:
    if not options["regex"]:
        regex = r"^(%s)?([A-Z]+[a-z1-9]*)+$" % options["private-prefix"]
    else:
        regex = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not re.match(regex, name):
        yield Problem(
            *positions_from_token(name),
            rule,
            "The inner class name '" + name + "' is not formated correctly."
        )
