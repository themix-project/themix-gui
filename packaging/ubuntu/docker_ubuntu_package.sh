#!/usr/bin/env bash
#set -x
set -euo pipefail

rebuild=0
for opt in $(getopt -l rebuild -o r -- "$@"); do
	if [[ "${opt}" = '--rebuild' ]] ; then
		rebuild=1
	fi
done

here=$(pwd)
srcdir="$(readlink -e "$(dirname "${0}")"/../..)"

old_srcdir=${srcdir}
srcdir=${old_srcdir}.ubuntu_build
echo "== Copying to temporary directory..."
sudo rm -fr "${srcdir}"
cp -prf "${old_srcdir}" "${srcdir}"
echo "== Removing unstaged git files:"
git -C "${srcdir}" clean -f -d -x

releases=('zesty' 'cosmic')
for release in "${releases[@]}" ; do
	if [[ ${release} = 'zesty' ]] ; then
		release_ver="17.04+"
	elif [[ ${release} = 'cosmic' ]] ; then
		release_ver="18.10+"
	fi
	echo
	echo ":: PACKAGING FOR ${release_ver}..."
	echo
	set -x
	cp "${srcdir}"/packaging/ubuntu/Dockerfile_"${release}" "${srcdir}"/Dockerfile
	container_is_running=1
	docker ps -a | grep oomox_ubuntu_"${release}"_build || container_is_running=
	if [[ -n "${container_is_running}" ]] ; then
		docker rm -v oomox_ubuntu_"${release}"_build
	fi
	if [[ ${rebuild} -eq 1 ]] ; then
		docker build -t oomox_ubuntu_"${release}"_build_image "${srcdir}"
	else
		(docker images | grep oomox_ubuntu_"${release}"_build_image) || docker build -t oomox_ubuntu_"${release}"_build_image "${srcdir}"
	fi
	docker run -t --name oomox_ubuntu_"${release}"_build -v "${srcdir}":/opt/oomox oomox_ubuntu_"${release}"_build_image
	docker cp oomox_ubuntu_"${release}"_build:/opt/oomox/ubuntu_package/oomox.deb "${here}"/
	mv "${here}"/oomox.deb "${here}"/oomox_"$(git describe)"_"${release_ver}".deb
	docker rm -v oomox_ubuntu_"${release}"_build
	rm "${srcdir}"/Dockerfile
done

sudo rm -fr "${srcdir}"

echo DOCKER DONE
exit 0
