#!/usr/bin/env bash
set -ueo pipefail

srcdir="$(readlink -e $(dirname ${0})/../..)"

_pkgdirname='ubuntu_package_1810'
if [[ -d ./${_pkgdirname} ]] ; then
	rm -r ./${_pkgdirname}
fi
mkdir ./${_pkgdirname}
pkgdir=$(readlink -e ./${_pkgdirname})

mkdir ${pkgdir}/DEBIAN
cp ${srcdir}/packaging/ubuntu/postinst ${pkgdir}/DEBIAN
cp ${srcdir}/packaging/ubuntu/control_1810 ${pkgdir}/DEBIAN/control

cd ${srcdir}
make DESTDIR="${pkgdir}" install

cd ${pkgdir}
dpkg-deb --build . oomox.deb

echo DEB PACKAGING DONE
exit 0
