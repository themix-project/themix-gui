#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

new_version=$1

#if [[ $(git status --porcelain 2>/dev/null| grep -c "^ [MD]") -gt 0 ]] ; then
	#echo
	#echo "   !!! You have uncommited changes: !!!"
	#echo
	#git status
	#exit 1
#fi

sed -i -e "s/pkgver=.*/pkgver=${new_version}/g" packaging/arch/PKGBUILD
sed -i -e "s/pkgrel=.*/pkgrel=1/g" packaging/arch/PKGBUILD
sed -i -e "s/^Version: .*/Version: ${new_version}-1~themixproject~zesty/" packaging/ubuntu/control
sed -i -e 's/"tag": ".*"/"tag": "'"${new_version}"'"/g' packaging/flatpak/com.github.actionless.oomox.json
git commit -am "chore: bump version to ${new_version}"
git tag -a "${new_version}"
