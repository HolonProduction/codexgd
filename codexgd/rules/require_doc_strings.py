"""require-doc-strings

Members should be documented using docstrings.
"""

from typing import List, cast

import regex

from codexgd.rule import rule
from codexgd.gdscript import (
    GDScriptCodex,
    ParseTree,
    Token,
    Problem,
    positions_from_element,
)


rule.doc(__doc__, {"private-prefix": "_"})


code: str = ""
doc_strings: List[int] = []


@rule.check(GDScriptCodex.plain_text)
def plain_text(p_code: str, _options):
    global code
    code = p_code
    return []


@rule.check(GDScriptCodex.comment)
def comment(comment: Token, _options):
    global doc_strings
    if comment.startswith("##"):
        doc_strings.append(cast(int, comment.line))
    return []


@rule.check(
    GDScriptCodex.parse_tree("class_var_stmt"), lambda x: x.children[0].children[0]
)
@rule.check(GDScriptCodex.parse_tree("func_def"), lambda x: x.children[0].children[0])
@rule.check(GDScriptCodex.parse_tree("class_def"), lambda x: x.children[0])
@rule.check(GDScriptCodex.parse_tree("signal_stmt"), lambda x: x.children[0])
def parse_tree(tree: ParseTree, options, extract_name):
    global doc_strings
    name = extract_name(tree)
    if options["private-prefix"] is None or not regex.match(
        f"^{options['private-prefix']}", name
    ):
        if tree.meta.line - 1 not in doc_strings:
            yield Problem(
                *positions_from_element(name),
                rule,
                f"The member '{name}' is not documented.",
            )
