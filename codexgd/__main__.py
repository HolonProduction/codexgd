"""CodexGD

A configurable and extendable Godot style analyzer.
CodexGD can also be used in your own python scripts
with an API that is more powerfull than this CLI.

Usage:
    codexgd <dir> [options]
    codexgd <codex> <gdscript>... [options]

Options:
    -h --help           Show this screen.
    -v --version        Show the current version.
    --encoding=codec    The encoding of the files. [default: "utf-8"]
    --load-unsafe-code  Load untrusted code from outside the CodexGD package if the codex file says so.
    --json              Output json data.
    --

Returns:
    0   The input conforms to the given codex file.
    1   The input does not conform to the give codex.
    2   During execution an exception occured.
"""

import os.path
import sys
import glob
import json
from docopt import docopt
from codexgd import CodexGDError
from codexgd.gdscript import GDScriptCodex
from codexgd.__about__ import __version__


def main():
    arguments = docopt(__doc__, version=__version__)

    if arguments["<dir>"]:
        try:
            with open(
                os.path.join(arguments["<dir>"], "codex.yml"),
                "r",
                encoding=arguments["--encoding"],
            ) as file:
                codex = GDScriptCodex(file, arguments["--load-unsafe-code"])
        except (FileExistsError, CodexGDError) as error:
            if not arguments["--json"]:
                print(error)
            sys.exit(2)
    elif arguments["<codex>"]:
        try:
            with open(
                arguments["<codex>"], "r", encoding=arguments["--encoding"]
            ) as file:
                codex = GDScriptCodex(file, arguments["--load-unsafe-code"])
        except (FileExistsError, CodexGDError) as error:
            if not arguments["--json"]:
                print(error)
            sys.exit(2)
    else:
        if not arguments["--json"]:
            print("No configuration was provided.")
        sys.exit(2)

    file_paths = []
    file_paths += arguments["<gdscript>"]

    if arguments["<dir>"]:
        file_paths += glob.glob(
            os.path.join(arguments["<dir>"], "**", "*.gd"), recursive=True
        )

    if arguments["--json"]:
        print("[", end="")

    found_problems = 0
    for file_path in file_paths:
        with open(file_path, "r", encoding=arguments["--encoding"]) as file:
            for problem in codex.check(file):
                if arguments["--json"]:
                    if found_problems > 0:
                        print(", ", end="")
                    print(
                        json.dumps(
                            {
                                "severity": problem.rule.severity,
                                "info": problem.info,
                                "file": file_path,
                                "start": problem.start,
                                "end": problem.end,
                                "rule": problem.rule.name,
                            }
                        ),
                        end="",
                    )
                else:
                    print(
                        problem.rule.severity.value.upper(),
                        ": ",
                        problem.info,
                        "\t",
                        os.path.realpath(file_path),
                        " Ln ",
                        problem.start[0],
                        ":",
                        problem.start[1],
                        " (",
                        problem.rule.name,
                        ")",
                        sep="",
                    )
                found_problems += 1

    if not arguments["--json"]:
        print(
            "\n" if found_problems > 0 else "",
            "CodexGD found ",
            str(found_problems),
            " problem",
            "s" if found_problems != 1 else "",
            " in ",
            str(len(file_paths)),
            " file",
            "s" if len(file_paths) > 1 else "",
            ".",
            " Go fix " + ("them" if found_problems > 1 else "it") + "!"
            if found_problems > 0
            else " \U0001f389",
            sep="",
        )
    else:
        print("]", end="")

    sys.exit(int(found_problems > 0))


if __name__ == "__main__":
    main()
