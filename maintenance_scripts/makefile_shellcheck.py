#!/usr/bin/python

import os
import subprocess  # nosec B404
import sys
import tempfile
from typing import Final

MAKEFILE: str = "./Makefile"
if len(sys.argv) > 1:
    MAKEFILE = sys.argv[1]

DEFAULT_ENCODING: Final = "utf-8"
MAKE_SHELL: Final = os.environ.get("MAKE_SHELL", "sh")
# SKIP_TARGETS_WITH_CHARS = ("%", )
SKIP_TARGETS_WITH_CHARS: Final = ("%", "/")
SKIP_TARGETS: Final = (".PHONY", ".PRECIOUS")


_ALL: Final = "all"


def get_targets() -> list[str]:
    lines = subprocess.check_output(  # nosec B603
        args=[
            "make",
            "--dry-run",
            f"--makefile={MAKEFILE}",
            "--print-data-base",
            "--no-builtin-rules",
            "--no-builtin-variables",
        ],
        encoding=DEFAULT_ENCODING,
    ).splitlines()
    not_a_target_comment = "# Not a target:"

    targets = []
    for idx, line in enumerate(lines):
        if lines[idx - 1] == not_a_target_comment:
            continue

        word = line.split(" ", maxsplit=1)[0]
        if not word.endswith(":"):
            continue

        skip = False
        for char in SKIP_TARGETS_WITH_CHARS:
            if char in word:
                skip = True
        if skip:
            continue

        target = word.rstrip(":")
        if target in SKIP_TARGETS:
            continue

        targets.append(target)
    targets = sorted(set(targets), reverse=True)

    # check it last:
    targets.remove(_ALL)
    targets.append(_ALL)
    return targets


def print_by_lines(text: str) -> None:
    for idx, line in enumerate(text.splitlines()):
        print(f"{idx + 1}: {line}")


def print_error_in_target(target: str) -> None:
    print(
        f"\n{'-' * 30}\n"
        f"ERROR in target `{target}`:"
        f"\n{'-' * 30}",
    )


def main() -> None:
    print("Starting the check...")
    targets = get_targets()
    if _ALL not in targets:
        print(f"ERROR: `{_ALL}` target is not defined.")
        sys.exit(1)

    print("\nMake targets:")
    for target in targets:
        print(f"  {target}")
        try:
            make_result = subprocess.check_output(  # nosec B603
                args=[
                    "make",
                    "--dry-run",
                    f"--makefile={MAKEFILE}",
                    target,
                ],
                encoding=DEFAULT_ENCODING,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            print_error_in_target(target)
            print_by_lines(err.output)
            sys.exit(1)
        with tempfile.NamedTemporaryFile("w", encoding=DEFAULT_ENCODING) as fobj:
            fobj.write(make_result)
            fobj.seek(0)
            try:
                subprocess.check_output(  # nosec B603
                    args=[
                        "shellcheck",
                        fobj.name,
                        f"--shell={MAKE_SHELL}",
                        "--color=always",
                    ],
                    encoding=DEFAULT_ENCODING,
                )
            except subprocess.CalledProcessError as err:
                print_error_in_target(target)
                print_by_lines(make_result)
                print(err.output.replace(fobj.name, f"{MAKEFILE}:{target}"))
                sys.exit(1)

    print("\n:: OK ::")


if __name__ == "__main__":
    main()
