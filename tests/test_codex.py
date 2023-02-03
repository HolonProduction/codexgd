from io import StringIO

import pytest

from codexgd import Codex
from codexgd.gdscript import GDScriptCodex
from codexgd.codex import ConfigurationError
from .common import config_file


@pytest.fixture(params=[GDScriptCodex, Codex])
def Implementation(request):
    return request.param


def test_empty_codex(config_file, Implementation):
    codex = Implementation(config_file(""""""))


def test_unsafe_loading(config_file, Implementation):
    config = """
rules:
    codexgd.rules.no_invalid_chars: "error"
"""
    try:
        codex = Implementation(config_file(config))
        assert False, "An rule was loaded without unsafe loading enabled."
    except:
        pass

    codex = Implementation(config_file(config), True)


def test_load_module_rules(config_file, Implementation):
    config = """
rules:
    codexgd.rules.no_invalid_chars: "error"
"""
    codex = Implementation(config_file(config), True)
    assert len(codex.rules) == 1
    assert codex.rules[0].name == "no-invalid-chars"

    codex = Implementation(StringIO(config), True)
    assert len(codex.rules) == 1
    assert codex.rules[0].name == "no-invalid-chars"


def test_load_relative_rules(config_file, Implementation):
    config = """
rules:
    .rules.custom_rule: "error"
"""
    codex = Implementation(config_file(config), True)
    assert len(codex.rules) == 1
    assert codex.rules[0].name == "custom-rule"

    try:
        codex = Implementation(StringIO(config), True)
        assert (
            False
        ), "Codex loaded from StringIO should raise an error if relative rules are used."
    except ConfigurationError:
        pass


@pytest.mark.parametrize(
    "config_str, expected",
    [
        (
            """rules:
    .rules.never_rule: "off" """,
            "off",
        ),
        (
            """rules:
    .rules.never_rule: "warn" """,
            "warn",
        ),
        (
            """rules:
    .rules.never_rule: "error" """,
            "error",
        ),
        (
            """rules:
    .rules.never_rule: 
        level: "off" """,
            "off",
        ),
        (
            """rules:
    .rules.never_rule: 
        level: "warn" """,
            "warn",
        ),
        (
            """rules:
    .rules.never_rule: 
        level: "error" """,
            "error",
        ),
    ],
)
def test_load_severity(config_str, expected, config_file, Implementation):
    codex = Implementation(config_file(config_str), True)
    assert len(codex.rules) == 1
    assert codex.rules[0].severity == expected


def test_load_invalid_option(Implementation):
    config = """
rules:
    codexgd.rules.no_invalid_chars:
        options:
            invalid-option: true
"""
    try:
        codex = Implementation(config, True)
        assert (
            True
        ), "A codex object should not accept options which a rule does not define."
    except ConfigurationError:
        pass


def test_notify(config_file, Implementation):
    config = """
rules:
    .rules.always_rule: "error"
"""
    codex = Implementation(config_file(config), True)
    assert len(codex.rules) == 1

    problems = list(codex.notify(Implementation.before_all))
    assert len(problems) == 1


def test_multiple_codexes(config_file, Implementation):
    config = """
rules:
    .rules.rule_with_state: "error"
"""
    codex1 = Implementation(config_file(config), True)
    codex2 = Implementation(config_file(config), True)
    assert codex1.rules[0] is not codex2.rules[0]

    problems = list(codex1.notify(Implementation.before_all)) + list(
        codex2.notify(Implementation.before_all)
    )
    assert len(problems) == 0
