#!/usr/bin/env bash
#set -x
set -euo pipefail

here=$(pwd)
srcdir="$(readlink -e $(dirname ${0})/../..)"

old_srcdir=${srcdir}
srcdir=${srcdir}.ubuntu_build
echo "== Copying to temporary directory..."
rm -fr ${srcdir}
cp -prf ${old_srcdir} ${srcdir}
echo "== Removing unstaged git files:"
git -C ${srcdir} clean -f -d -x

cp ${srcdir}/packaging/ubuntu/Dockerfile ${srcdir}/
container_is_running=1
docker ps -a | grep oomox_ubuntu_zesty_build || container_is_running=
if [[ ! -z "${container_is_running}" ]] ; then
	docker rm -v oomox_ubuntu_zesty_build
fi
(docker images | grep oomox_ubuntu_zesty_build_image) || docker build -t oomox_ubuntu_zesty_build_image ${srcdir}
docker run -t --name oomox_ubuntu_zesty_build -v ${srcdir}:/opt/oomox oomox_ubuntu_zesty_build_image
docker cp oomox_ubuntu_zesty_build:/opt/oomox/ubuntu_package/oomox.deb ${here}/oomox_$(git describe).deb
docker rm -v oomox_ubuntu_zesty_build
rm ${srcdir}/Dockerfile
sudo rm -fr ${srcdir}

echo DOCKER DONE
exit 0
