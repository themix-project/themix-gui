#!/usr/bin/python

import os
import subprocess  # nosec B404
import sys

MAKEFILE = "./Makefile"
if len(sys.argv) > 1:
    MAKEFILE = sys.argv[1]

MAKE_SHELL = os.environ.get("MAKE_SHELL", "sh")
DEFAULT_ENCODING = "utf-8"


def get_targets() -> list[str]:
    targets = subprocess.check_output(
        args=(
            "make"
            " --dry-run"
            f' --makefile="{MAKEFILE}"'
            " --print-data-base"
            " --no-builtin-rules"
            " --no-builtin-variables"
            " | grep -E '^[^. ]+:' -o"
            # " | sort"
            " | sort -r"
            " | uniq"
            " | sed 's/:$//g'"
        ),
        shell=True,
        encoding=DEFAULT_ENCODING
    ).splitlines()

    targets.remove("Makefile")
    # # check it last:
    # targets.remove("all")
    # targets.append("all")
    return targets


def main() -> None:
    print("Starting the check...")
    targets = get_targets()
    if "all" not in targets:
        print("ERROR: `all` target is not defined.")
        sys.exit(1)

    print("\nMake targets:")
    for target in targets:
        print(f"  {target}")
        make_cmd = f'make --dry-run --makefile="{MAKEFILE}" "{target}"'
        try:
            subprocess.check_output(  # nosec B603
                args=[
                    "bash", "-c",
                    f'set -ue ; shellcheck <({make_cmd}) --shell="{MAKE_SHELL}" --color=always'
                ],
                encoding=DEFAULT_ENCODING,
            )
        except subprocess.CalledProcessError as err:
            make_result = subprocess.check_output(
                args=make_cmd,
                shell=True,
                encoding=DEFAULT_ENCODING,
            )
            print(f"\n{target}:")
            for idx, line in enumerate(make_result.splitlines()):
                print(f"{idx+1}: {line}")
            print(err.output)
            sys.exit(1)

    print("\n:: OK ::")


if __name__ == "__main__":
    main()
