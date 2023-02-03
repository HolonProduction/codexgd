<img src="./assets/banner.svg">

<!--# <img src="./plugins/godot/icon.svg" style="vertical-align: top; height: 1.3em" /> CodexGD - *Give your code a dress code*.-->
<br>

[![Godot 4.x](https://img.shields.io/static/v1?label=Godot&message=4.x&color=grey&logo=godotengine&logoColor=white&labelColor=478cbf)](https://godotengine.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen.svg)](https://github.com/PyCQA/pylint)

> :construction: CodexGD is currently in development. If you are looking for a way to enforce the official style guide you should have a look at [gdtoolkit](https://github.com/Scony/godot-gdscript-toolkit). I am in fact using gdtoolkit internally myself. It has its own linter that does a very good job when it comes to the official style. The main reason for me to develop this package is that I have my own GDScript style and extending gdlint is not very simple.

CodexGD is a configurable and extendable Godot style analyzer written in python. CodexGD comes with a set of rules that you can configure to your liking but it also gives you an easy way to write own rules using python.

## :electric_plug: Installation
In the future CodexGD will be available via PyPi and the Godot Asset Lib. Until then you will have to set it up manually. Start by cloning this repo. 
To use the backend you will need a python 3.11 installation. Install the cloned repo as python module by calling the following command in the cloned repo's root folder.
```shell
> python -m pip install -e .
```
It is recommended to install CodexGD into a [virtual environment](https://docs.python.org/3/tutorial/venv.html). When doing this the codexgd command will not be available globaly. You will also have to configure your venv when using the editor plugin (more on this later).

To install the editor plugin copy the `plugins/godot/addons/codexgd` folder into your project's `addons` folder. You should also create a `codex.yml` file at the root of your project before enabeling it.

## :computer: General Usage
CodexGD is built around a `codex.yml` file which you will use to configure your style. The codex file will define the rules that will be used on your code. Here is a simple example:
```yml
extends: "official"             # Use the official style as base.

rules:
    no-invalid-chars: "warn"    # Downgrade the severity of the no-invalid-chars rule.
```

The easiest way to use CodexGD is to use the provided CLI.
```shell
> python -m codexgd project_directory
```
CodexGD will look for a `codex.yml` file in the provided directory and apply it to all `.gd` files in the directory.

You can also use the package from your own python scripts. The API is centered around `Codex` objects which you can create by providing a `codex.yml` file.

```python
from codexgd.gdscript import GDScriptCodex

with open("codex.yml", "r") as file:
    codex = GDScriptCodex(file)

with open("file.gd", "r") as file:
    for problem in codex.check(file):
        print(problem)
```

## :jigsaw: Editor Plugin
> :construction: The editor plugin is in development and not yet feature complete.

CodexGD comes with an editor integration. It will display the problems that CodexGD detected in the script editor. It relies on the CLI, therefore an installation of the python package is needed. If the python package was installed globaly the plugin should work out of the box. Otherwise you will have to select the path to the `codexgd` command in the EditorSettings `"codexgd/general/command_path"`. The file will be located in your venv folder in the `scripts` subfolder. It should be named `codexgd` with an executable file ending.

State of the editor integration:
- [x] Display problems in the script editor.
- [ ] Support for embedded scripts.
- [ ] Handle errors during the execution. (The plugin may fail silently.)
- [ ] Display overlapping problems in a good way.
- [ ] Help with the setup of a `codex.yml` file.
- [ ] Provide a simple way to see all problems of the project.

## :wrench: Configuration

### :scroll: The codex file
The codex file is a yaml file that may contain the following keys.  

**`extends`**  
Which style to use as base. Currently only `"official"` and `"recommended"` are supported values. You may overwrite the rule settings with the `rules` key.

**`rules`**  
A list of rules with associated options.
```yaml
rules:
    no-invalid-chars:
        level: "warn"   # The severity of the rule. Allowed values: off, warn, error
        options:
            codec: "utf8"
    # If no options are specified the severity may be specified directly.
    require-extends: "error"
```
There are multiple ways to specify which rule is meant. You can use the rule name as above but this is only possible if the rule was loaded before. You can use the name `no-invalid-chars` because the `official` base file loaded it. To load a rule you specify the python module name. You can use a global module specification like `codexgd.rules.no_invalid_chars`. You may also use relative module specifications. In this case codexgd will try to resolve them as relative path from your codex file. In this way you can load custom rules which are located in your project directory.
```yaml
rules:
    .rules.custom_rule: "error"
```
The code above will load a rule from `res://rules/custom_rule.py` given your codex file is located at `res://codex.yml`.
> :warning: CodexGD will not load rules from outside the codexgd package by default because an untrusted project may execute code on your machine in this way. Pass the `--load-unsafe-code` option to the CLI to confirm that you know about the risks.

**`variables`**  
A dictionary of named values which may be used in the options of rules later. This allows to unify values which are needed by multiple rules like the prefix of private methods. The name of a variable should start with `<` and end with `>`.
```yaml
variables:
    <private-prefix>: "_"
rules:
    function-names:
        level: "warn"
        options:
            private-prefix: <private-prefix>
```

### :heavy_check_mark: Rules
The rules contain documentation comments explaining them. Currently implemented rules can be found at `"codexgd/rules"`.

### :see_no_evil: Ignore comments
CodexGD alows you to disable certain rules in gdscript files by using special comments.
Ignore comments are not meant to be placed on the same line with gdscript code.

```python
# Ignore only the next line.
# codexgd-ignore

# Disable rules until they are enabled again.
# codexgd-disable

# Enable rules.
# codexgd-enable
```
All ignore comments may optionally recieve a list of rule names. If no rule names are provided all rules will be affected.
```python
# codexgd-disable: function-names, no-invalid-chars
# codexgd-enable: no-invalid-chars
```

Problems are ignored based on the line on which they beginn. Therefore problems which span the complete file can only be ignored by a `codexgd-disable` statement on the first line.

It is considered good practice to state the reason for disabeling the rule behind the ignore comment in a rational and calm manner...
```python
# codexgd-ignore: no-invalid-chars    Why would CodexGD not allow me to use utf8 inside of strings?! What is the developer even thinking!
```
