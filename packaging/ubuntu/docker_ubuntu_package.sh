#!/usr/bin/env bash
set -euo pipefail

here=$(pwd)
srcdir="$(readlink -e $(dirname ${0})/../..)"

cp ${srcdir}/packaging/ubuntu/Dockerfile ${srcdir}/
(docker images | grep oomox_ubuntu_zesty_build_image) || docker build -t oomox_ubuntu_zesty_build_image ${srcdir}
docker run -t --name oomox_ubuntu_zesty_build -v ${srcdir}:/opt/oomox oomox_ubuntu_zesty_build_image
docker cp oomox_ubuntu_zesty_build:/opt/oomox/ubuntu_package/oomox.deb ${here}
docker rm -v oomox_ubuntu_zesty_build
rm ${srcdir}/Dockerfile
sudo rm -fr ${srcdir}/ubuntu_package

echo DOCKER DONE
exit 0
