"""no-invalid-chars

Do not use characters that cannot be encoded with a certain codec.

Good:
```gdscript
func hello_world():
    pass
```
Bad:
```
func hello_wörld():
    pass
```

Options:
- codec = "ascii"  
Only chars which can be encoded with this codec will be accepted. Accepts any valid python codec name.
- string-codec = "utf8"  
Strings may contain characters that can be encoded with this codec as well.
"""
from typing import cast

from lark import Token

from codexgd.rule import rule, Options
from codexgd.gdscript import GDScriptCodex, Problem, ParseTree


rule.doc(__doc__, {"codec": "ascii", "string-codec": "utf8"})


code: str
guarded = []


@rule.check(GDScriptCodex.plain_text)
def plain_text(text: str, _options: Options):
    global code
    code = text
    return []


@rule.check(GDScriptCodex.parse_tree("string"))
def parse_tree_string(tree: ParseTree, options: Options):
    content = cast(Token, tree.children[0])
    line_index = cast(int, content.line)
    column = cast(int, content.column)

    for line in content.splitlines():
        for char in line:
            try:
                char.encode(str(options["string-codec"]))
                guarded.append((line_index, column))
            except UnicodeEncodeError:
                pass
            column += 1
        line_index += 1
        column = 1

    return []


@rule.check(GDScriptCodex.after_all)
def after_all(options: Options):
    line_index = 1
    column = 1

    for line in code.splitlines():
        for char in line:
            if (line_index, column) not in guarded:
                try:
                    char.encode(str(options["codec"]))
                except UnicodeEncodeError:
                    yield Problem(
                        (line_index, column),
                        (line_index, column + 1),
                        rule,
                        "Using the not "
                        + str(options["codec"])
                        + " encodable char '"
                        + char
                        + "'.",
                    )
            column += 1
        line_index += 1
        column = 1
