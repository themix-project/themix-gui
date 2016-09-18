#!/bin/bash

update_changes_file() {
	local LATEST_STABLE_RELEASE
	LATEST_STABLE_RELEASE=$(git describe --tags $(git rev-list --tags --max-count=1))

	[[ -f CHANGES ]] && mv CHANGES CHANGES.old

	{ git log \
		--pretty=format:"[%ai] %<(69,trunc) %s %><(15) %aN {%h}" \
		--cherry-pick "${LATEST_STABLE_RELEASE}...HEAD"; } > CHANGES

	[[ -f CHANGES.old ]] && cat CHANGES.old >> CHANGES && rm CHANGES.old

	git add CHANGES
	git commit -m 'RELEASE PREP :: Update CHANGES file.'
	git push
}


case $1 in
	changes)
		update_changes_file
		exit $?
	;;

	*)
		exit 0
	;;
esac
