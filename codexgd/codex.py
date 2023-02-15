from typing import List, Iterable, Dict, Optional, Callable, Tuple
from typing_extensions import TypeVarTuple, Any, Unpack

from abc import ABC

import os
import sys
import importlib.util
from importlib.machinery import ModuleSpec
import yaml

from .rule import Rule, Severity
from .callback import Callback
from . import rule

from .exceptions import CodexGDError
from .problem import Problem


class ConfigurationError(CodexGDError):
    """Errors related to loading the configuration."""


Parameter = TypeVarTuple("Parameter")


class Codex(ABC):
    """Applies rules onto given data."""

    rules: List[Rule]
    before_all = Callback[Unpack[Tuple[()]]]()
    after_all = Callback[Unpack[Tuple[()]]]()

    def __init__(self, codex_file, unsafe: bool = False, generate_cache: bool = False):
        self.rules = []
        self._load_file(codex_file, unsafe, generate_cache)

    def notify(
        self, callback: Callback[Unpack[Parameter]], *values: Unpack[Parameter]
    ) -> Iterable[Problem]:
        for r in self.rules:
            if r.severity == Severity.OFF:
                continue

            if callback in r.callbacks:
                for m in r.callbacks[callback]:
                    for p in m(*values, r.options):
                        yield p

    def _load_file(
        self,
        file,
        unsafe: bool = False,
        generate_cache: bool = False,
        variables: Optional[Dict[str, Any]] = None,
    ):
        if variables is None:
            variables = {}
        file_name = file.name if hasattr(file, "name") else None
        data = yaml.safe_load(file)
        if not data:
            return

        if "variables" in data.keys():
            for variable in data["variables"].keys():
                # Variables from higher files take precedence.
                if not variable in variables.keys():
                    variables[variable] = data["variables"][variable]

        if "extends" in data.keys():
            # Load builtin rulesets unsafe to import builtin rules.
            if data["extends"] == "official":
                with open(
                    os.path.join(os.path.dirname(__file__), "presets", "official.yml"),
                    "r",
                    encoding="utf8",
                ) as extends:
                    self._load_file(
                        extends,
                        True,
                        True,
                        variables,
                    )
            elif data["extends"] == "recommended":
                with open(
                    os.path.join(
                        os.path.dirname(__file__), "presets", "recommended.yml"
                    ),
                    "r",
                    encoding="utf8",
                ) as extends:
                    self._load_file(
                        extends,
                        True,
                        True,
                        variables,
                    )

        if "rules" in data.keys():

            def compare(spec: Optional[ModuleSpec]) -> Callable[[Rule], bool]:
                def inner(new_rule: Rule) -> bool:
                    return new_rule.name == rule_key or (
                        os.path.normpath(os.path.realpath(spec.origin))
                        == new_rule.origin
                        if spec and spec.origin
                        else False
                    )

                return inner

            for rule_key in data["rules"].keys():
                if rule_key[0] == ".":
                    # Resolve relative rules as files.
                    if not file_name:
                        raise ConfigurationError(
                            "Relative rule imports cannot be used in codex files that were not loaded from the file system."
                        )
                    spec = importlib.util.spec_from_file_location(
                        rule_key,
                        os.path.join(os.path.dirname(file_name), *rule_key.split("."))
                        + ".py",
                    )
                else:
                    spec = importlib.util.find_spec(rule_key)

                loaded: List[Rule] = list(filter(compare(spec), self.rules))

                if len(loaded) < 1:
                    if spec and spec.loader:
                        if unsafe:
                            old = sys.dont_write_bytecode
                            sys.dont_write_bytecode = not generate_cache

                            rule.rule = Rule()
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            if rule.rule.origin == "":
                                raise ConfigurationError(
                                    "The module '" + rule_key + "' is no valid rule."
                                )

                            self.rules.append(rule.rule)
                            rule.rule = None
                            sys.dont_write_bytecode = old
                        else:
                            raise ConfigurationError(
                                "The module '"
                                + rule_key
                                + "' will not be loaded because it could contain untrusted code. If you want to use unofficial rules you have to enable unsafe loading."
                            )
                    else:
                        raise ConfigurationError(
                            "'"
                            + rule_key
                            + "' is not the name of a module or a loaded rule."
                        )

                loaded_rule: Rule = list(filter(compare(spec), self.rules))[0]

                rule_data = data["rules"][rule_key]
                if isinstance(rule_data, str):
                    loaded_rule.severity = Severity(data["rules"][rule_key])
                elif isinstance(rule_data, dict):
                    if "level" in rule_data.keys():
                        loaded_rule.severity = Severity(rule_data["level"])
                    if "options" in rule_data.keys():
                        for option in rule_data["options"]:
                            if option not in loaded_rule.options:
                                raise ConfigurationError(
                                    "'"
                                    + option
                                    + "' is not a valid option of the rule '"
                                    + loaded_rule.name
                                    + "'."
                                )

                            if rule_data["options"][option] in variables:
                                value = variables[rule_data["options"][option]]
                            else:
                                value = rule_data["options"][option]
                            loaded_rule.options[option] = value
