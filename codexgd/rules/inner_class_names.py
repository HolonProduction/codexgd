"""inner-class-names

Inner class names should use PascalCase which may have a prefix to indicate private classes.

Good:
```gdscript
class PascalCase
class _PrivateClass
```
Bad:
```gdscript
class snake_case
```

Options:
- `private-prefix = "_"`  
The prefix for private classes. Supports regex.
**Use the corresponding variable! (Except you know what you are doing.)**
- `regex = None`  
Provide a custom regex for class names. When this is set all other options will be ignored.
"""
from typing import cast

import regex

from lark import Token

from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, positions_from_element
from codexgd.rule import rule, Options
from codexgd.rules.common import PASCAL_CASE


rule.doc(__doc__, {"private-prefix": "_", "regex": None})


@rule.check(GDScriptCodex.parse_tree("class_def"))
def parse_tree_element(tree: ParseTree, options: Options):
    if not options["regex"]:
        pattern = rf"^({options['private-prefix']})?{PASCAL_CASE}$"
    else:
        pattern = str(options["regex"])

    name = cast(Token, tree.children[0])
    if not regex.match(pattern, name):
        yield Problem(
            *positions_from_element(name),
            rule,
            "The inner class name '" + name + "' is not formated correctly.",
        )
