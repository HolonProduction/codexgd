from codexgd.rule import rule, Problem
from codexgd.gdscript import GDScriptCodex, COMPLETE_FILE

rule("custom-rule", "Test custom rule loading.")

found_class = False

@rule.check(GDScriptCodex.parse_tree("class_def"))
def parse_tree_class_def(tree, options):
    global found_class
    found_class = not found_class
    return []

@rule.check(GDScriptCodex.after_all)
def after_all(options):
    global found_class
    if not found_class:
        yield Problem(*COMPLETE_FILE, rule, "The file does not contain any classes.")