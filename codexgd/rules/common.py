from typing import Union, cast, Optional

from lark import Tree, ParseTree, Token

SNAKE_CASE = r"[\p{Ll}1-9]+(_[\p{Ll}1-9]+)*"
PASCAL_CASE = r"([\p{Lu}1-9][\p{Ll}1-9]*)+"
CAMEL_CASE = r"[\p{Ll}1-9]+([\p{Lu}1-9][\p{Ll}1-9]*)*"
CONSTANT_CASE = r"[\p{Lu}1-9]+(_[\p{Lu}1-9]+)*"
KEBAB_CASE = r"[\p{Ll}1-9]+(-[\p{Ll}1-9]+)*"


def is_type(tree: Union[ParseTree, Token]) -> bool:
    if isinstance(tree, Tree):
        if tree.data == "expr":
            return is_type(tree.children[0])
        if tree.data == "standalone_call" and tree.children[0] in ["preload", "load"]:
            file = extract_string(tree.children[1])
            if file and file.endswith(".gd"):
                return True
    return False


def extract_string(tree: Union[ParseTree, Token]) -> Optional[str]:
    if isinstance(tree, Token):
        if tree.type == "REGULAR_STRING":
            return tree[1:-1]
        elif tree.type == "LONG_STRING":
            return tree[3:-3]
    else:
        if tree.data == "string":
            return extract_string(tree.children[0])
    return None
