#!/usr/bin/env bash

filter=cat
if [[ "${1:-}" = '-c' ]] ; then
	filter="grep -v -i -e style -e travis -e docker -e chore -e test -e revert -e screensh -e merge"
	shift
fi

git log \
	--pretty=tformat:"%Cred%D%Creset %ad %Cgreen%h %Cblue%an %Creset%s" \
	--date='format:%Y-%m-%d' \
	--color=always \
	$(git tag | grep -v gtk | sort -V | tail -n1)~1.. \
	$@ \
| $filter
