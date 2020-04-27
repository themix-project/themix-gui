#!/usr/bin/env bash
set -ueo pipefail

for submodule in $(git config --file .gitmodules --get-regexp path | awk '{ print $2 }') ; do
	hashes=$(git diff | grep "${submodule}" -A 3 | grep -e "^[+-]Subproject" | cut -d ' ' -f3 | cut -d- -f1 | paste -sd '%' -) || hashes=''
	if [[ -n "${hashes}" ]] ; then
		echo
		echo "SUBMODULE [7m${submodule}[30m[m:"
		echo "================================================================================="
		hash1=$(cut -d% -f1 <<< "${hashes}")
		hash2=$(cut -d% -f2 <<< "${hashes}")
		if [[ "${hash1}" = "${hash2}" ]] ; then
			git -C "${submodule}"/ status
		else
			echo "${hashes}"
			git -C "${submodule}"/ log --oneline "${hash1}".."${hash2}"
		fi
	fi
done
