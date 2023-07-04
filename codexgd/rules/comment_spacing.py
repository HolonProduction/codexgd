"""comment-spacing

Comments should start with a space.
"""

from codexgd.rule import rule
from codexgd.gdscript import GDScriptCodex, Token, Problem, positions_from_element


rule.doc(__doc__)


@rule.check(GDScriptCodex.comment)
def comment(tree: Token, _options):
    if tree.startswith("##"):
        content = tree[2:]
    else:
        content = tree[1:]

    if len(content) > 0 and content[0] != " ":
        yield Problem(
            *positions_from_element(tree),
            rule,
            "Comments should start with a space. If this is code that was commented out, take it as a reminder to review the necessity of the code.",
        )
    elif len(content) > 1 and content[1] == " ":
        yield Problem(
            *positions_from_element(tree),
            rule,
            "Comments should start with only one space.",
        )
