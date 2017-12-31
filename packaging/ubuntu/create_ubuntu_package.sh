#!/usr/bin/env bash
set -ueo pipefail

srcdir="$(readlink -e $(dirname ${0})/../..)"

if [[ -d ./ubuntu_package ]] ; then
	rm -r ./ubuntu_package
fi
mkdir ./ubuntu_package
pkgdir=$(readlink -e ./ubuntu_package)

mkdir ${pkgdir}/DEBIAN
cp ${srcdir}/packaging/ubuntu/{control,postinst} ${pkgdir}/DEBIAN

${srcdir}/packaging/install.sh ${srcdir} ${pkgdir}

cd ${pkgdir}
dpkg-deb --build . oomox.deb

echo DONE
exit 0
