from codexgd.gdscript import GDScriptCodex
from .common import config_file
from io import StringIO
import pytest


@pytest.mark.parametrize(
    "config_str, code, n",
    [
        # require-extends
        ("""rules: {codexgd.rules.require_extends: "error"}""", """""", 1),
        (
            """rules: {codexgd.rules.require_extends: "error"}""",
            """func test():
    pass
""",
            1,
        ),
        (
            """rules: {codexgd.rules.require_extends: "error"}""",
            """extends Object""",
            0,
        ),
        (
            """rules: {codexgd.rules.require_extends: "error"}""",
            """extends "res://script.gd"
func test():
    pass
""",
            0,
        ),
        # no-invalid-chars
        ("""rules: {codexgd.rules.no_invalid_chars: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.no_invalid_chars: "error"}""",
            """class T: pass
# valid \n""",
            0,
        ),
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "ascii"}}}""",
            """class T: pass
# not valid ä \n""",
            1,
        ),
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "utf8"}}}""",
            """class T: pass
# valid ö \n""",
            0,
        ),
        # function-names
        ("""rules: {codexgd.rules.function_names: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.function_names: {level: "error", options: {private-prefix: "_"}}}""",
            """
func _virtual(): pass
func _private(): pass
func valid_with_nr2(): pass
""",
            0,
        ),
        (
            """rules: {codexgd.rules.function_names: {level: "error", options: {private-prefix: "_"}}}""",
            """
func __private(): pass
func wrongName(): pass
func WrongAsWell(): pass
""",
            3,
        ),
        (
            """rules: {codexgd.rules.function_names: {level: "error", options: {private-prefix: "__"}}}""",
            """
func _virtual(): pass
func __private(): pass
""",
            0,
        ),
        (
            """rules: {codexgd.rules.function_names: {level: "error", options: {connected-pascal-case: true}}}""",
            """
func on_SignalName(): pass
func _on_SignalName_private(): pass
""",
            0,
        ),
        (
            """rules: {codexgd.rules.function_names: {level: "error", options: {connected-pascal-case: false}}}""",
            """
func on_SignalName(): pass
func _on_SignalName_private(): pass
""",
            2,
        ),
        # inner-class-names
        ("""rules: {codexgd.rules.inner_class_names: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.inner_class_names: "error"}""",
            """
class _PrivateClass: pass
class PublicClass: pass
""",
            0,
        ),
        (
            """rules: {codexgd.rules.inner_class_names: "error"}""",
            """
class invalid_class: pass
class Mixed_Class: pass
class __InvalidPrefix: pass
""",
            3,
        ),
        (
            """rules:
    codexgd.rules.inner_class_names:
        level: "error"
        options:
            private-prefix: "__"
""",
            """
class __PrivateClass: pass
""",
            0,
        ),
        (
            """rules:
    codexgd.rules.inner_class_names:
        level: "error"
        options:
            private-prefix: "__"
""",
            """
class _PrivateClass: pass
""",
            1,
        ),
    ],
)
def test_rule(config_str, code, n, config_file):
    codex = GDScriptCodex(config_file(config_str), True)
    problems = list(codex.check(StringIO(code)))
    assert len(problems) == n
