#!/bin/bash
set -ue

result=$(
	grep -REn "^[a-zA-Z_]+ = [^'\"].*" "$@" --color=always \
	| grep -Ev \
		-e ': Final' \
		\
		-e ' =.*\|' \
		-e ' = [a-zA-Z_]+\[' \
		-e ' = str[^(]' \
		-e TypeVar \
		-e namedtuple \
		\
		-e 'create_logger\(|running_as_root|sudo' \
	| sort
)
echo -n "$result"
exit "$(test "$result" = "" && echo 0 || echo 1)"
