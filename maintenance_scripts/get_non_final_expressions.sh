#!/bin/bash
set -ue

result=$(
	grep -REn "^[a-zA-Z_]+ = " oomox_gui --color=always \
	| grep -Ev \
		-e ': Final' \
		\
		-e '\|' \
		-e '(dict|list)\[' \
		-e TypeVar \
		-e Sequence \
		-e namedtuple \
		\
		-e 'HexColor' \
		-e 'ColorScheme' \
	| sort
)
echo -n "$result"
exit "$(test "$result" = "" && echo 0 || echo 1)"
