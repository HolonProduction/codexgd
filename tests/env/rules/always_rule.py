from codexgd.rule import rule
from codexgd import Codex, Problem
from codexgd.gdscript import COMPLETE_FILE


rule("always-rule", "Will always add exactly one problem.")


@rule.check(Codex.before_all, True)
def before_all(_options, fail: bool):
    if fail:
        yield Problem(
            *COMPLETE_FILE,
            rule,
            "This is a test problem. It will always apear and you can't do a "
            "thing about it \U0001f608",
        )
