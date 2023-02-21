"""line-length

Lines should not be too long.

Options:
- `max-length = 100`  
The maximum length that a line may have.
"""
from typing import cast

from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex

rule.doc(__doc__, {"max-length": 100})


@rule.check(GDScriptCodex.plain_text)
def plain_text(text: str, options: Options):
    for index, line in enumerate(text.splitlines(), start=1):
        if len(line) > cast(int, options["max-length"]):
            yield Problem((index, -1), (index, -1), rule, "The line is too long.")
