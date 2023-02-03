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
- codec = "ASCII"
Only chars which can be encoded with this codec will be accepted. Accepts any valid python codec name.
"""

from typing import Iterable

from codexgd.rule import rule, Options
from codexgd.gdscript import GDScriptCodex, Problem


rule.doc(__doc__, {"codec": "ascii"})


@rule.check(GDScriptCodex.plain_text)
def plain_text(text: str, options: Options) -> Iterable[Problem]:
    res = []

    line_index = 1
    column = 1

    for line in text.splitlines():
        for char in line:
            try:
                char.encode(str(options["codec"]))
            except UnicodeEncodeError:
                res.append(
                    Problem(
                        (line_index, column),
                        (line_index, column + 1),
                        rule,
                        "Using the not "
                        + str(options["codec"])
                        + " encodable char '"
                        + char
                        + "'.",
                    )
                )
            column += 1
        line_index += 1
        column = 1

    return res
