from .common import config_file
from codexgd.gdscript import GDScriptCodex
from io import StringIO
import pytest


@pytest.mark.parametrize(
    "code, counts",
    [
        ("""""", (1, 1)),
        (
            """# codexgd-disable
var a""",
            (0, 1),
        ),
        (
            """# codexgd-disable
func Invalid():
    pass
# codexgd-enable
func Invalid2():
    pass
""",
            (1, 3),
        ),
        (
            """# codexgd-enable
var a""",
            (1, 1),
        ),
        (
            """# codexgd-disable: function-names

func Invalid():
    pass""",
            (1, 2),
        ),
        (
            """# codexgd-disable
# codexgd-enable: function-names
func Invalid():
    pass""",
            (1, 2),
        ),
        (
            """# codexgd-ignore
func Invalid():
    pass""",
            (1, 2),
        ),
        (
            """# codexgd-ignore: function-names
func Invalid():
    pass""",
            (1, 2),
        ),
    ],
)
def test_ignore_comments(code: str, counts, config_file):
    config = """rules:
    .rules.always_rule: "error"
    codexgd.rules.function_names: "error"
"""
    codex = GDScriptCodex(config_file(config), True)
    p_with = list(codex.check(StringIO(code)))
    p_without = list(codex.check_without_ignore(StringIO(code)))
    assert (len(p_with), len(p_without)) == counts
