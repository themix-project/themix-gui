#!/usr/bin/env python

import argparse
import subprocess  # nosec B404
import sys
import tempfile
from dataclasses import dataclass
from typing import Final

DEFAULT_ENCODING: Final = "utf-8"
SKIP_TARGETS_WITH_CHARS: Final = ("%", )
PHONY: Final = ".PHONY"
PRECIOUS: Final = ".PRECIOUS"
SKIP_TARGETS: Final = [PHONY, PRECIOUS]
_ALL: Final = "all"
DEFAULT_SHELL: Final = "sh"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Makefile shellcheck",
    )
    parser.add_argument(
        "makefile",
        nargs="?",
        default="./Makefile",
        metavar="Makefile",
        help="path to Makefile to check",
    )
    parser.add_argument(
        "-s", "--skip",
        action="append",
        default=[],
        metavar="TARGET",
        help="make target to skip (arg could be used multiple times)",
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="list make targets",
    )

    parser.add_argument(
        "--shell",
        help="make shell",
    )
    parser.add_argument(
        "-e", "--exclude",
        default="",
        metavar="CODE1,CODE2..",
        help=(
            "Shellcheck: Exclude types of warnings"
        ),
    )
    parser.add_argument(
        "-P", "--source-path",
        default="",
        metavar="SOURCEPATHS",
        help=(
            "Shellcheck: Specify path when looking for sourced files"
            " (\"SCRIPTDIR\" for script's dir)"
        ),
    )
    parser.add_argument(
        "-x", "--external-sources", "--external",
        action="store_true",
        help="Shellcheck: allow external source-s",
    )
    return parser.parse_args()


@dataclass(kw_only=True)
class MakefileMetadata:
    targets: list[str]
    make_shell: str | None
    phony: list[str]
    precious: list[str]

    @classmethod
    def open(cls, args: argparse.Namespace) -> "MakefileMetadata":
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
        phony = []
        precious = []
        for idx, line in enumerate(lines):
            if not make_shell:
                words = line.replace("\t", " ").split(" ")
                if (
                        (len(words) == 3)  # noqa: PLR2004:
                        and (words[0] == "SHELL")
                        and (words[1] == ":=")
                ):
                    make_shell = words[2]

            if lines[idx - 1] == not_a_target_comment:
                continue

            word = line.replace("\t", " ").split(" ", maxsplit=1)[0]
            if not word.endswith(":"):
                continue

            skip = False
            for char in SKIP_TARGETS_WITH_CHARS:
                if char in word:
                    skip = True
            if skip:
                continue

            target = word.rstrip(":")
            if target == PHONY:
                phony = line.split(" ")[1:]
            elif target == PRECIOUS:
                precious = line.split(" ")[1:]
            if target in SKIP_TARGETS + args.skip:
                continue

            targets.append(target)
        targets = sorted(set(targets))

        # check it last:
        targets.remove(_ALL)
        targets.append(_ALL)
        return cls(
            targets=targets, make_shell=make_shell, phony=phony, precious=precious,
        )


def print_by_lines(text: str) -> None:
    for idx, line in enumerate(text.splitlines()):
        print(f"{idx + 1}: {line}")


def print_error_in_target(target: str) -> None:
    print(
        f"\n{'-' * 30}\n"
        f"ERROR in target `{target}`:"
        f"\n{'-' * 30}",
    )


def print_targets(makefile_metadata: MakefileMetadata) -> None:
    for target in makefile_metadata.targets:
        print(
            f"{target}"
            f"{' (PHONY)' if target in makefile_metadata.phony else ''}"
            f"{' (PRECIOUS)' if target in makefile_metadata.precious else ''}",
        )


class ShellCheckError(Exception):
    pass


def shellcheck_maketarget(
        target: str, makefile_metadata: MakefileMetadata, args: argparse.Namespace,
) -> None:
    make_shell = makefile_metadata.make_shell
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
        shellcheck_args = [
            "shellcheck",
            fobj.name,
            f"--shell={args.shell or make_shell or DEFAULT_SHELL}",
            "--color=always",
        ]
        shellcheck_args.extend([
            f"--{arg_name.replace('_', '-')}"
            for arg_name in ("external_sources", )
            if getattr(args, arg_name)
        ])
        shellcheck_args.extend([
            f"--{arg_name.replace('_', '-')}={value}"
            for arg_name in ("source_path", "exclude")
            if (value := getattr(args, arg_name))
        ])
        try:
            subprocess.check_output(  # nosec B603
                args=shellcheck_args,
                encoding=DEFAULT_ENCODING,
            )
        except subprocess.CalledProcessError as err:
            print_error_in_target(target)
            print_by_lines(make_result)
            raise ShellCheckError(
                err.output.replace(fobj.name, f"{args.makefile}:{target}"),
            ) from err


def main() -> None:
    args = parse_args()
    # print(args)
    print("Starting the check...")
    makefile_metadata = MakefileMetadata.open(args)
    targets = makefile_metadata.targets
    if args.list:
        print_targets(makefile_metadata)
        sys.exit(0)
    if _ALL not in targets:
        print(f"ERROR: `{_ALL}` target is not defined.")
        sys.exit(1)

    print("\nMake targets:")
    for target in targets:
        print(f"  {target}")
        try:
            shellcheck_maketarget(target=target, makefile_metadata=makefile_metadata, args=args)
        except ShellCheckError as exc:
            print(exc)
            sys.exit(1)

    print("\n:: OK ::")


if __name__ == "__main__":
    main()
