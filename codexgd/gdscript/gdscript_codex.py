from typing import Iterable, TextIO, List, cast, Dict, Tuple

from io import StringIO
import re

from lark import Tree, Visitor, Token
from gdtoolkit.parser import parser

from ..codex import Codex
from ..problem import Problem
from ..callback import Callback, DynamicCallback


IgnoreMap = Dict[str, List[Tuple[str, int]]]
ParseTree = Tree[Token]


class ParseTreeCallback(DynamicCallback[ParseTree, str]):
    """Dynamic callback for subscribing to certain parse tree elements."""


class _ParseTreeVisitor(Visitor):
    codex: "GDScriptCodex"
    problems: List[Problem]

    def __init__(self, codex: "GDScriptCodex") -> None:
        self.codex = codex
        self.problems = []

    def __default__(self, tree: ParseTree):
        for i in self.codex.notify(ParseTreeCallback(tree.data), tree):
            self.problems.append(i)


class GDScriptCodex(Codex):
    """Enforce rules on GDScript code."""

    plain_text = Callback[str]()
    parse_tree = ParseTreeCallback.factory
    comment = Callback[Token]()

    def check(self, file: TextIO) -> Iterable[Problem]:
        code = file.read()
        ignore_map = self._construct_ignore_map(code)

        yield from self._apply_ignore_map(
            ignore_map, self.check_without_ignore(StringIO(code))
        )

    def check_without_ignore(self, file: TextIO) -> Iterable[Problem]:
        code = file.read()

        yield from self.notify(self.before_all)
        yield from self.notify(self.plain_text, code)

        comments = self._get_comment_list(code)
        for comment in comments:
            yield from self.notify(self.comment, comment)

        parse_tree = self._build_parse_tree(code)

        visitor = _ParseTreeVisitor(self)
        visitor.visit(parse_tree)
        yield from visitor.problems

        yield from self.notify(self.after_all)

    def _build_parse_tree(self, code: str) -> ParseTree:
        return parser.parse(code, True)

    def _get_comment_list(self, code: str) -> List[Token]:
        tree = parser.parse_comments(code)
        return cast(List[Token], tree.children)

    def _construct_ignore_map(self, code: str) -> IgnoreMap:
        comments = parser.parse_comments(code)

        ignore_map: IgnoreMap = {}

        def add(rule_name: str):
            """Makes sure that a key for the rule exists."""
            if rule_name not in ignore_map:
                ignore_map[rule_name] = []

        comment_pattern = re.compile(
            r"codexgd-(?P<type>disable|enable|ignore)(:(?P<rules>\s*[^,\s]+(\s*,\s*[^,\s]+)*))?",
        )

        for comment in comments.children:
            match = comment_pattern.search(
                cast(Token, comment),
            )
            if match:
                rules = match.group("rules")
                if rules:
                    for rule in rules.split(","):
                        rule_name = rule.strip()
                        add(rule_name)
                        ignore_map[rule_name].append(
                            (match.group("type"), cast(int, cast(Token, comment).line))
                        )
                else:
                    for rule in self.rules:
                        add(rule.name)
                        ignore_map[rule.name].append(
                            (match.group("type"), cast(int, cast(Token, comment).line))
                        )

        last_line = len(code.split("\n"))
        for i in ignore_map.items():
            i[1].append(("enable", last_line))

        return ignore_map

    def _apply_ignore_map(
        self, ignore_map: IgnoreMap, problems: Iterable[Problem]
    ) -> Iterable[Problem]:
        def resolve_start(start):
            return start[0] if start[0] > 0 else 1

        for problem in problems:
            if problem.rule.name not in ignore_map:
                yield problem
                continue
            enabled = True
            for step in ignore_map[problem.rule.name]:
                if step[0] == "ignore":
                    if step[1] != resolve_start(problem.start) - 1:
                        yield problem
                    break
                if step[1] <= resolve_start(problem.start):
                    enabled = step[0] == "enable"
                if step[1] >= resolve_start(problem.start):
                    if enabled:
                        yield problem
                    break
