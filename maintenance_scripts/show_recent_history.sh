#!/usr/bin/env bash
set -euo pipefail

filter="cat"
if [[ "${1:-}" = '-c' ]] ; then
	filter="grep -v -i -E \
		-e (typing|typehint|coverage|github|docker|vulture) \
		-e actionless\s[^[:print:]]\[m(doc|chore|test|style|Revert|Merge|refactor)\
		-e [^[:print:]]\[31m[[:print:]]+[^[:print:]]\[m
	"
	shift
fi

result=$(git log \
	--pretty=tformat:"%Cred%D%Creset %ad %Cgreen%h %Cblue%an %Creset%s" \
	--date='format:%Y-%m-%d' \
	--color=always \
	"$(git tag | grep -v gtk | sort -V | tail -n1)"~1.. \
	"$@" \
)

if [[ "${filter}" = "cat" ]] ; then
	echo "$result"
else
	echo "Notable changes:"
	echo "$result" | $filter
	echo
	echo "Submodule changes:"
	grep submodule <<< "$result"
	echo
	echo "Previous release:"
	echo "$result" | tail -n1
fi
