"""end-with-newline

End your file with a newline.

Good:
```gdscript
func hello_world():
    pass

```
Bad:
```gdscript
func hello_world():
    pass
```
"""
from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex


rule.doc(__doc__)


@rule.check(GDScriptCodex.plain_text)
def plain_text(text: str, _options: Options):
    if text.endswith("\n\n"):
        yield Problem(
            (-1, 0),
            (-1, -1),
            rule,
            "The file should end with exactly one new line.",
        )
    elif not text.endswith("\n"):
        yield Problem((-1, 0), (-1, -1), rule, "The file should end with a new line.")
