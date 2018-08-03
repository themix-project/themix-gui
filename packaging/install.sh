#!/usr/bin/env bash
#set -x
set -ueo pipefail

srcdir=$(readlink -e "$1")
#pkgdir=$(readlink -e "$2")
pkgdir="${2}"

cd "${srcdir}"
make DESTDIR="${pkgdir}" install

exit 0
