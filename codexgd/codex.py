from typing import List, Iterable, Dict, Optional, Callable, Tuple

from abc import ABC
import os
import sys
import importlib.util
from importlib.machinery import ModuleSpec

from typing_extensions import TypeVarTuple, Any, Unpack

import yaml

from .rule import Rule, Severity
from .callback import Callback
from . import rule as rule_module

from .exceptions import CodexGDError
from .problem import Problem


class ConfigurationError(CodexGDError):
    """Errors related to loading the configuration."""


Parameter = TypeVarTuple("Parameter")


class Codex(ABC):
    """Applies rules onto given data."""

    rules: List[Rule]
    variables: Dict[str, Any]
    before_all = Callback[Unpack[Tuple[()]]]()
    after_all = Callback[Unpack[Tuple[()]]]()

    def __init__(self, codex_file, unsafe: bool = False, generate_cache: bool = False):
        self.rules = []
        self.variables = {}
        self._load_file(codex_file, unsafe, generate_cache)

    def notify(
        self, callback: Callback[Unpack[Parameter]], *values: Unpack[Parameter]
    ) -> Iterable[Problem]:
        for rule in self.rules:
            if rule.severity == Severity.OFF:
                continue

            if callback in rule.callbacks:
                for method in rule.callbacks[callback]:
                    for problem in method(*values, rule.options):
                        yield problem

    def _load_variables(self, data: Dict) -> None:
        if "variables" not in data.keys():
            return

        for variable in data["variables"].keys():
            # Variables from higher files take precedence.
            if not variable in self.variables:
                self.variables[variable] = data["variables"][variable]

    def _load_inheritance(self, data: Dict) -> None:
        if "extends" not in data.keys():
            return

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
                )
        elif data["extends"] == "recommended":
            with open(
                os.path.join(os.path.dirname(__file__), "presets", "recommended.yml"),
                "r",
                encoding="utf8",
            ) as extends:
                self._load_file(
                    extends,
                    True,
                    True,
                )

    def _get_spec_from_rule_key(
        self, rule_key: str, file_name: Optional[str]
    ) -> Optional[ModuleSpec]:
        if rule_key.startswith("."):
            # Resolve relative rules as files.
            if not file_name:
                raise ConfigurationError(
                    "Relative rule imports cannot be used in codex "
                    "files that were not loaded from the file system."
                )
            return importlib.util.spec_from_file_location(
                rule_key,
                os.path.join(os.path.dirname(file_name), *rule_key.split(".")) + ".py",
            )
        return importlib.util.find_spec(rule_key)

    def _load_rule(
        self,
        rule_data: Tuple[str, Any],
        file_name: Optional[str],
        unsafe: bool,
        generate_cache: bool,
    ) -> None:
        def compare(spec: Optional[ModuleSpec]) -> Callable[[Rule], bool]:
            def inner(new_rule: Rule) -> bool:
                return new_rule.name == rule_data[0] or (
                    os.path.normpath(os.path.realpath(spec.origin)) == new_rule.origin
                    if spec and spec.origin
                    else False
                )

            return inner

        spec = self._get_spec_from_rule_key(rule_data[0], file_name)

        loaded: List[Rule] = list(filter(compare(spec), self.rules))

        if len(loaded) < 1:
            if not (spec and spec.loader):
                raise ConfigurationError(
                    f"'{rule_data[0]}' is not the name of a module or a loaded rule."
                )

            if not unsafe:
                raise ConfigurationError(
                    f"The module '{rule_data[0]}' will not be loaded because it could untrusted "
                    "code. If you want to use unofficial rules you have to enable unsafe loading."
                )

            old = sys.dont_write_bytecode
            sys.dont_write_bytecode = not generate_cache

            rule_module.rule = Rule()
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if rule_module.rule.origin == "":
                raise ConfigurationError(
                    f"The module '{rule_data[0]}' is no valid rule."
                )

            self.rules.append(rule_module.rule)
            rule_module.rule = None
            sys.dont_write_bytecode = old

        loaded_rule: Rule = list(filter(compare(spec), self.rules))[0]

        if isinstance(rule_data[1], str):
            loaded_rule.severity = Severity(rule_data[1])
        elif isinstance(rule_data[1], dict):
            if "level" in rule_data[1].keys():
                loaded_rule.severity = Severity(rule_data[1]["level"])
            if "options" in rule_data[1].keys():
                for option in rule_data[1]["options"]:
                    if option not in loaded_rule.options:
                        raise ConfigurationError(
                            f"'{option}' is not a valid option of the rule '{loaded_rule.name}'."
                        )

                    if rule_data[1]["options"][option] in self.variables:
                        value = self.variables[rule_data[1]["options"][option]]
                    else:
                        value = rule_data[1]["options"][option]
                    loaded_rule.options[option] = value

    def _load_rules(
        self, data: Dict, file_name: Optional[str], unsafe: bool, generate_cache: bool
    ) -> None:
        if "rules" not in data.keys():
            return

        for rule_key in data["rules"].keys():
            self._load_rule(
                (rule_key, data["rules"][rule_key]), file_name, unsafe, generate_cache
            )

    def _load_file(
        self,
        file,
        unsafe: bool = False,
        generate_cache: bool = False,
    ):
        file_name = file.name if hasattr(file, "name") else None
        data = yaml.safe_load(file)
        if not data:
            return

        self._load_variables(data)
        self._load_inheritance(data)
        self._load_rules(data, file_name, unsafe, generate_cache)
