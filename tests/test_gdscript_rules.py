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
        # line-length
        ("""rules: {codexgd.rules.line_length: "error"}""", """""", 0),
        ("""rules: {codexgd.rules.line_length: "error"}""", """var a = 10""", 0),
        (
            """rules: {codexgd.rules.line_length: "error"}""",
            """var a = 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000""",
            0,
        ),
        (
            """rules: {codexgd.rules.line_length: "error"}""",
            """var a = 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001""",
            1,
        ),
        # parameter-names
        ("""rules: {codexgd.rules.parameter_names: "error"}""", """""", 0),
        ("""rules: {codexgd.rules.parameter_names: "error"}""", """signal a\n""", 0),
        ("""rules: {codexgd.rules.parameter_names: "error"}""", """signal a(a)\n""", 0),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(hello_world)\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(a: int)\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(hello_world: int)\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(a_2d)\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(a_2d: int)\n""",
            0,
        ),
        ("""rules: {codexgd.rules.parameter_names: "error"}""", """signal a(_a)""", 1),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(_a: int)\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(HelloWorld)\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """signal a(HelloWorld: int)\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a: int): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a: int = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a := 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(_a): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(_a = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(_a: int): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(_a: int = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(_a := 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_b): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_b = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_b: int): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_b: int = 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_b := 0): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_ = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_: int): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_: int = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(a_ := 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(aH): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(aH = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(aH: int): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(aH: int = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(aH := 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(HelloWorld): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(HelloWorld = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(HelloWorld: int): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(HelloWorld: int = 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """func a(HelloWorld := 0): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """var name:
    set(v): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """var name:
    set(_v): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """var name:
    set(hello_world): pass\n""",
            0,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """var name:
    set(T): pass\n""",
            1,
        ),
        (
            """rules: {codexgd.rules.parameter_names: "error"}""",
            """var name:
    set(HelloWorld): pass\n""",
            1,
        ),
        # signal-names
        ("""rules: {codexgd.rules.signal_names: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal hello_world""",
            0,
        ),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal hello_world()""",
            0,
        ),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal hello_world(test)""",
            0,
        ),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal hello_world(test: int)""",
            0,
        ),
        ("""rules: {codexgd.rules.signal_names: "error"}""", """signal a""", 0),
        ("""rules: {codexgd.rules.signal_names: "error"}""", """signal abc""", 0),
        ("""rules: {codexgd.rules.signal_names: "error"}""", """signal abc2d""", 0),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal SignalName""",
            1,
        ),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal Signal_Name""",
            1,
        ),
        (
            """rules: {codexgd.rules.signal_names: "error"}""",
            """signal SIGNAL_NAME_2D""",
            1,
        ),
        # variable-names
        (
            """rules: {codexgd.rules.variable_names: "error"}""",
            """var hi
var hi = 1
const HI = 1
var hi: int
var hi := 1
const HI := 1
var Hi: int = preload('''test.gd''')
const Hi: int = preload('''test.gd''')
var Hi: int = preload('test.gd')
const Hi: int = preload('test.gd')
var Hi = preload("test.gd")
const Hi = preload("test.gd")
var Hi : = preload(\"\"\"test.gd\"\"\")
const Hi : = preload(\"\"\"test.gd\"\"\")

func p():
    var hi
    var Hi = preload("t.gd")
    const Hi = preload("t.gd")
    var hi: int
    var hi: int = 1
    const HI: int = 1
    const HI := 1
    var hi := 1
""",
            0,
        ),
        (
            """rules: {codexgd.rules.variable_names: "error"}""",
            """var Hi
var Hi = 1
const hi = 1
var Hi: int
var Hi := 1
const hi := 1
var hi: int = preload('''test.gd''')
const hi: int = preload('''test.gd''')
var hi: int = preload('test.gd')
const hi: int = preload('test.gd')
var hi = preload("test.gd")
const hi = preload("test.gd")
var hi : = preload(\"\"\"test.gd\"\"\")
const hi : = preload(\"\"\"test.gd\"\"\")
const HELLO__WORLD := 1

func p():
    var Hi
    var hi = preload("t.gd")
    const hi = preload("t.gd")
    var Hi: int
    var Hi: int = 1
    const Hi: int = 1
    var Hi := 1
""",
            22,
        ),
        (
            """rules: {codexgd.rules.variable_names: "error"}""",
            """var _hi
var hi
var Hi = preload("t.gd")
var _hi
var _Hi = preload("t.gd")
var hello_world
var HelloWorld = preload("t.gd")
var a_b_c
var _ABV = preload("t.gd")
var node2d
var Node2D = preload("t.gd")
var node_2d
const HELLO_WORLD = 1
const _HELLO_WORLD = 2
const H = 1
const A_B_C = 1
const HelloWorld = preload("t.gd")
const _HelloWorld = preload("t.gd")
func p():
    var hi
    var Hi = preload("t.gd")
    var _hi
    var _Hi = preload("t.gd")
    var hello_world
    var HelloWorld = preload("t.gd")
    var a_b_c
    var _ABV = preload("t.gd")
    var node2d
    var Node2D = preload("t.gd")
    var node_2d
""",
            0,
        ),
        # trailing-commas
        ("""rules: {codexgd.rules.trailing_commas: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.trailing_commas: "error"}""",
            """var a = ["1", 2, 3]
var b = [
    "1",
    2,
    3,
]
var c = {"a": 1, "b": 2, 3: "c"}
var d = {
    "a": 1,
    "b": 2,
    3: "c",
}
enum {A, B, C}
enum {
    A,
    B,
    C,
}
""",
            0,
        ),
        (
            """rules: {codexgd.rules.trailing_commas: "error"}""",
            """var a = ["1", 2, 3,]
var b = [
    "1",
    2,
    3
]
var c = {"a": 1, "b": 2, 3: "c",}
var d = {
    "a": 1,
    "b": 2,
    3: "c"
}
enum {A, B, C,}
enum {
    A,
    B,
    C
}
""",
            6,
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
        # class-names
        ("""rules: {codexgd.rules.class_names: "error"}""", """""", 0),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """
var test := 10
""",
            0,
        ),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """class_name HelloWorld""",
            0,
        ),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """class_name World2D""",
            0,
        ),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """class_name WRONG_NAME""",
            1,
        ),
        ("""rules: {codexgd.rules.class_names: "error"}""", """class_name nope""", 1),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """class_name _NotValidIGuess""",
            1,
        ),
        (
            """rules: {codexgd.rules.class_names: "error"}""",
            """class_name the_name""",
            1,
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
        # enum-names
        ("""rules: {codexgd.rules.enum_names: "error"}""", """""", 0),
        ("""rules: {codexgd.rules.enum_names: "error"}""", """enum {}""", 0),
        ("""rules: {codexgd.rules.enum_names: "error"}""", """enum Test {}""", 0),
        ("""rules: {codexgd.rules.enum_names: "error"}""", """enum Test2D {}""", 0),
        ("""rules: {codexgd.rules.enum_names: "error"}""", """enum TestTest {}""", 0),
        ("""rules: {codexgd.rules.enum_names: "error"}""", """enum _TestTest {}""", 0),
        (
            """rules: {codexgd.rules.enum_names: {level: "error", options: {private-prefix: ""}}}""",
            """enum _TestTest {}""",
            1,
        ),
        (
            """rules: {codexgd.rules.enum_names: {level: "error", options: {private-prefix: ""}}}""",
            """enum TestTest {}""",
            0,
        ),
        (
            """rules: {codexgd.rules.enum_names: {level: "error", options: {private-prefix: "__"}}}""",
            """enum TestTest {}""",
            0,
        ),
        (
            """rules: {codexgd.rules.enum_names: {level: "error", options: {private-prefix: "__"}}}""",
            """enum _TestTest {}""",
            1,
        ),
        (
            """rules: {codexgd.rules.enum_names: {level: "error", options: {private-prefix: "__"}}}""",
            """enum __TestTest {}""",
            0,
        ),
    ],
)
def test_rule(config_str, code, n, config_file):
    codex = GDScriptCodex(config_file(config_str), True)
    problems = list(codex.check(StringIO(code)))
    assert len(problems) == n
