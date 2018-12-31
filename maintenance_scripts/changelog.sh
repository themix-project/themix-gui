#!/usr/bin/env bash

# This file is licensed under GPLv3, see https://www.gnu.org/licenses/

set -euo pipefail
IFS=$'\n\t'

for tag in $(git tag | sort -V) ; do
	echo -e '\n'
	git tag -n --format '%(taggerdate)' "$tag"
	echo '-------------------------------------------------'
	git tag -n999 "$tag"
done
