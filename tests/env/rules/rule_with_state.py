from codexgd.rule import rule, Problem
from codexgd import Codex
from codexgd.gdscript import COMPLETE_FILE

rule("rule-with-state", "Rule with state.")

state = False


@rule.check(Codex.before_all)
def parse_tree_class_def(options):
    global state
    if state:
        yield Problem(
            *COMPLETE_FILE, rule, "State leaks accross different rule instances."
        )
    state = True
