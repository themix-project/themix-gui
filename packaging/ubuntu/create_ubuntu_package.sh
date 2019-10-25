#!/usr/bin/env bash
set -ueo pipefail

control_file="${1}"

srcdir="$(readlink -e "$(dirname "${0}")"/../..)"

_pkgdirname='ubuntu_package'
if [[ -d ./${_pkgdirname} ]] ; then
	rm -r ./${_pkgdirname}
fi
mkdir ./${_pkgdirname}
pkgdir=$(readlink -e ./${_pkgdirname})

mkdir "${pkgdir}"/DEBIAN
cp "${srcdir}"/packaging/ubuntu/postinst "${pkgdir}"/DEBIAN
cp "${srcdir}"/packaging/ubuntu/"${control_file}" "${pkgdir}"/DEBIAN/control

cd "${srcdir}"
make DESTDIR="${pkgdir}" install

cd "${pkgdir}"
dpkg-deb --build . oomox.deb
apt install -y --no-install-recommends ./oomox.deb

echo DEB PACKAGING DONE
exit 0
