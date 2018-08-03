#!/usr/bin/env bash

filter=cat
if [[ "${1:-}" = '-c' ]] ; then
	filter="grep -v -i -E -e (typing|typehint|coverage|travis|docker) -e actionless.*(chore|test|style|doc|Revert|Merge)"
	shift
fi

git log \
	--pretty=tformat:"%Cred%D%Creset %ad %Cgreen%h %Cblue%an %Creset%s" \
	--date='format:%Y-%m-%d' \
	--color=always \
	$(git tag | grep -v gtk | sort -V | tail -n1)~1.. \
	$@ \
| $filter
