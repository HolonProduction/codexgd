"""enum-names

Enums should be named in PascalCase which may have a prefix to indicate private enums.

Good:
```gdscript
enum SomeImportantStuff {}
enum _PrivateState {}
```
Bad:
```gdscript
enum COLLECTION_OF_CONSTANTS {}

Options:
- `private-prefix = "_"`  
The prefix for private enums. Supports regex.
**Use the corresponding variable! (Except you know what you are doing.)**
- `regex = None`  
Provide a custom regex for enum names. When this is set all other options will be ignored.
```
"""
from typing import cast
import regex

from lark import Token

from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex, ParseTree, positions_from_element
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
            *positions_from_element(name),
            rule,
            f"The enum name '{name}' is not formated correctly.",
        )
