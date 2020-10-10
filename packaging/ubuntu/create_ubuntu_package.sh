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
cp "${srcdir}"/packaging/ubuntu/prerm    "${pkgdir}"/DEBIAN
cp "${srcdir}"/packaging/ubuntu/"${control_file}" "${pkgdir}"/DEBIAN/control

cd "${srcdir}"
make DESTDIR="${pkgdir}" install install_theme_arc

cd "${pkgdir}"
fakeroot dpkg-deb --build . oomox.deb
if [[ "${2:-}" = "--install" ]] ; then
	apt install -y --no-install-recommends ./oomox.deb
fi

echo DEB PACKAGING DONE
exit 0
