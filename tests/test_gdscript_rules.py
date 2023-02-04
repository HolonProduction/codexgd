from codexgd.gdscript import GDScriptCodex
from .common import config_file
from io import StringIO
import pytest


@pytest.mark.parametrize(
    "config_str, code, n",
    [
        # end-with-newline
        ("""rules: {codexgd.rules.end_with_newline: "error"}""", """""", 1),
        (
            """rules: {codexgd.rules.end_with_newline: "error"}""",
            """
""",
            0,
        ),
        ("""rules: {codexgd.rules.end_with_newline: "error"}""", """var a = "h" """, 1),
        (
            """rules: {codexgd.rules.end_with_newline: "error"}""",
            """var a = "h"
""",
            0,
        ),
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
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "ascii", "string-codec": "utf8"}}}""",
            """class T:
                var test = "Hello Wörld"
""",
            0,
        ),
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "ascii", "string-codec": "utf8"}}}""",
            """class T:
                var test = "Hello Wörld"
# invalid ä \n""",
            1,
        ),
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "ascii", "string-codec": "ascii"}}}""",
            """class T:
    var test = "Hello Wörld"

# invalid ä \n""",
            2,
        ),
        (
            """rules: {codexgd.rules.no_invalid_chars: {level: "error", options: {codec: "ascii", "string-codec": "ascii"}}}""",
            """class T:
    var t1 = "Hello Wörld"
    var t2 = &"Hello Wärld"
    var t3 = ^"ß"
""",
            3,
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
