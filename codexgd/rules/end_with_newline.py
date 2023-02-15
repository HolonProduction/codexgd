"""end-with-newline

End your file with a newline.
"""
from codexgd.rule import rule, Problem, Options
from codexgd.gdscript import GDScriptCodex


rule.doc(__doc__)


@rule.check(GDScriptCodex.plain_text)
def before_all(code: str, _options: Options):
    if len(code) == 0 or code[-1] != "\n":
        yield Problem(
            (len(code.splitlines()), -1),
            (-1, -1),
            rule,
            "Files should end with a newline.",
        )
