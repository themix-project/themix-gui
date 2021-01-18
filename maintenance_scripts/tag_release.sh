#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'


new_version=$1
aur_dev_repo_root=~/build/


if [[ $(git status --porcelain 2>/dev/null| grep -c "^ [MD]") -gt 0 ]] ; then
	echo
	echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	echo "!!    You have uncommitted changes:    !!"
	echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	echo
	git status

	echo
	echo "?????????????????????????????????????????"
	echo "??    Do you want to proceed? [y/N]    ??"
	echo "?????????????????????????????????????????"
	echo -n "> "
	read -r answer
	echo
	if [[ "${answer}" != "y" ]] ; then
		exit 1
	fi
	answer=
fi

./maintenance_scripts/show_recent_history.sh -c || true


echo
echo "*******************************"
echo "**    Updating version...    **"
echo "*******************************"
echo

pkgbuilds=(
		packaging/arch/PKGBUILD_full
		packaging/arch/PKGBUILD_full_git
		packaging/arch/PKGBUILD_gui
		packaging/arch/PKGBUILD_import_image
		packaging/arch/PKGBUILD_migration
		packaging/arch/PKGBUILD_old
)
for pkgbuild_path in "${pkgbuilds[@]}"; do
	sed -i -e "s/pkgver=.*/pkgver=${new_version}/g" "$pkgbuild_path"
	sed -i -e "s/pkgrel=.*/pkgrel=1/g" "$pkgbuild_path"
done

sed -i -e "s/^Version: .*/Version: ${new_version}-1~themixproject~zesty/" packaging/ubuntu/control
sed -i -e "s/^Version: .*/Version: ${new_version}-1~themixproject~cosmic/" packaging/ubuntu/control_1810
sed -i -e 's/"tag": ".*"/"tag": "'"${new_version}"'"/g' packaging/flatpak/com.github.themix_project.Oomox.json
sed -i -e 's/<release .*\/>/<release date="'"$(date +"%Y-%m-%d")"'" version="'"$new_version"'"\/>/g' packaging/com.github.themix_project.Oomox.appdata.xml

echo
echo "??????????????????????????????????????????????????????????????????????"
echo "??    Confirm pushing ${new_version} to Oomox GitHub repo? [y/N]    ??"
echo "??????????????????????????????????????????????????????????????????????"
echo -n "> "
read -r answer
echo
if [[ "${answer}" = "y" ]] ; then
	git add \
		"${pkgbuilds[@]}" \
		packaging/ubuntu/control \
		packaging/ubuntu/control_1810 \
		packaging/flatpak/com.github.themix_project.Oomox.json \
		packaging/com.github.themix_project.Oomox.appdata.xml
	git commit -m "chore: bump version to ${new_version}" || true
	git tag -a "${new_version}"
	git push origin HEAD
	git push origin "${new_version}"
fi
answer=

update_aur_pkg(){
	aur_pkg_name="$1"
	pkgbuild_name="$2"

	aur_dev_repo_dir="${aur_dev_repo_root}/${aur_pkg_name}"

	echo
	echo "***************************************"
	echo "**    Updating ${aur_pkg_name} AUR PKBUILD...    **"
	echo "***************************************"
	echo
	./maintenance_scripts/changelog.sh > "${aur_dev_repo_dir}"/CHANGELOG
	cp ./packaging/arch/"$pkgbuild_name" "${aur_dev_repo_dir}"/PKGBUILD
	cd "${aur_dev_repo_dir}"
	makepkg --printsrcinfo > .SRCINFO


	echo
	echo "??????????????????????????????????????????????????"
	echo "??    Confirm push to ${aur_pkg_name} AUR? [y/N]    ??"
	echo "??????????????????????????????????????????????????"
	echo -n "> "
	read -r answer
	echo
	if [[ "${answer}" = "y" ]] ; then
		git add PKGBUILD .SRCINFO CHANGELOG
		git commit -m "update to ${new_version}"
		git push origin HEAD
	fi
	answer=

	cd -
}

update_aur_pkg oomox-git PKGBUILD_migration
update_aur_pkg themix-full-git PKGBUILD_full_git
update_aur_pkg themix-gui-git PKGBUILD_gui
update_aur_pkg themix-import-images-git PKGBUILD_import_image

echo
echo '$$$$$$$$$$$$$$$$$$$$$$$$$'
echo '$$    Full Success!    $$'
echo '$$$$$$$$$$$$$$$$$$$$$$$$$'

exit 0
