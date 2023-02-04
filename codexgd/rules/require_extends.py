"""require-extends

Each file has to use the `extends` statement.
"""

from codexgd.gdscript import GDScriptCodex, Problem, ParseTree, COMPLETE_FILE
from codexgd.rule import rule, Options


rule.doc(__doc__, {})


found_extends_statement: bool = False


@rule.check(GDScriptCodex.parse_tree("extends_stmt"))
def parse_tree_extends(_tree: ParseTree, _options: Options):
    # pylint: disable-next=invalid-name
    global found_extends_statement
    found_extends_statement = True
    return []


@rule.check(GDScriptCodex.after_all)
def after_all(_options: Options):
    if not found_extends_statement:
        yield Problem(
            *COMPLETE_FILE,
            rule,
            "The file does not clearly declare its inheritance using the `extends` statement.",
        )
