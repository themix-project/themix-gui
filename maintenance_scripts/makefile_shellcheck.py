#!/usr/bin/env python

import argparse
import subprocess  # nosec B404
import sys
import tempfile
from typing import Final

DEFAULT_ENCODING: Final = "utf-8"
# SKIP_TARGETS_WITH_CHARS = ("%", )
SKIP_TARGETS_WITH_CHARS: Final = ("%", "/")
SKIP_TARGETS: Final = [".PHONY", ".PRECIOUS"]


_ALL: Final = "all"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Makefile shellcheck",
    )
    parser.add_argument(
        "makefile",
        nargs="?",
        default="./Makefile",
        help="path to Makefile to check",
    )
    parser.add_argument(
        "-s", "--skip",
        action="append",
        default=[],
        help="make target to skip (arg could be used multiple times)",
    )
    parser.add_argument(
        "--shell",
        nargs="?",
        const="sh",
        default="sh",
        help="make shell",
    )
    return parser.parse_args()


def get_targets(args: argparse.Namespace) -> tuple[list[str], str | None]:
    lines = subprocess.check_output(  # nosec B603
        args=[
            "make",
            "--dry-run",
            f"--makefile={args.makefile}",
            "--print-data-base",
            "--no-builtin-rules",
            "--no-builtin-variables",
        ],
        encoding=DEFAULT_ENCODING,
    ).splitlines()
    not_a_target_comment = "# Not a target:"

    make_shell: str | None = None

    targets = []
    for idx, line in enumerate(lines):
        if not make_shell:
            words = line.split(" ")
            if (len(words) == 3) and (words[0] == "SHELL") and (words[1] == ":="):  # noqa: PLR2004:
                make_shell = words[2]

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
        if target in SKIP_TARGETS + args.skip:
            continue

        targets.append(target)
    targets = sorted(set(targets), reverse=True)

    # check it last:
    targets.remove(_ALL)
    targets.append(_ALL)
    return targets, make_shell


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
    args = parse_args()
    print("Starting the check...")
    targets, make_shell = get_targets(args)
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
                    f"--makefile={args.makefile}",
                    target,
                ],
                encoding=DEFAULT_ENCODING,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            print_error_in_target(target)
            print_by_lines(err.output)
            sys.exit(1)
        make_result = "\n".join(
            line
            for line in make_result.splitlines()
            if not line.startswith("make[1]")
        )
        with tempfile.NamedTemporaryFile("w", encoding=DEFAULT_ENCODING) as fobj:
            fobj.write(make_result)
            fobj.seek(0)
            try:
                subprocess.check_output(  # nosec B603
                    args=[
                        "shellcheck",
                        fobj.name,
                        f"--shell={make_shell or args.shell}",
                        "--color=always",
                    ],
                    encoding=DEFAULT_ENCODING,
                )
            except subprocess.CalledProcessError as err:
                print_error_in_target(target)
                print_by_lines(make_result)
                print(err.output.replace(fobj.name, f"{args.makefile}:{target}"))
                sys.exit(1)

    print("\n:: OK ::")


if __name__ == "__main__":
    main()
