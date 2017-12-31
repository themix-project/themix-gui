#!/usr/bin/env bash
set -ueo pipefail

# @TODO: mb rewrite it as a Makefile

srcdir=$1
pkgdir=$2

if [[ -d ${pkgdir}/opt/oomox ]] ; then
	rm -r ${pkgdir}/opt/oomox
fi
mkdir -p ${pkgdir}/opt/oomox

cd ${srcdir}
make -f po.mk install

cp -prf \
	./CREDITS \
	./LICENSE \
	./README.md \
	./colors \
	./gui.sh \
	./locale \
	./oomox_gui \
	./po \
		${pkgdir}/opt/oomox

mkdir ${pkgdir}/opt/oomox/gtk-theme
cd ./gtk-theme
cp -prf \
	./CHANGES \
	./CREDITS \
	./LICENSE \
	./Makefile \
	./README.md \
	./change_color.sh \
	./scripts \
	./src \
		${pkgdir}/opt/oomox/gtk-theme
cd ..

mkdir ${pkgdir}/opt/oomox/materia-theme
cd ./materia-theme
cp -prf \
	./COPYING \
	./HACKING.md \
	./README.md \
	./change_color.sh \
	./install.sh \
	./parse-sass.sh \
	./scripts \
	./src \
		${pkgdir}/opt/oomox/materia-theme
cd ..

mkdir ${pkgdir}/opt/oomox/archdroid-icon-theme
cd ./archdroid-icon-theme
cp -prf \
	./archdroid-icon-theme \
	./LICENSE \
	./README.md \
	./change_color.sh \
	./copyright \
		${pkgdir}/opt/oomox/archdroid-icon-theme
cd ..

mkdir ${pkgdir}/opt/oomox/gnome-colors-icon-theme
cd ./gnome-colors-icon-theme
cp -prf \
	./gnome-colors \
	./README.md \
	./change_color.sh \
		${pkgdir}/opt/oomox/gnome-colors-icon-theme
cd ..

mkdir ${pkgdir}/opt/oomox/oomoxify
cd ./oomoxify
cp -prf \
	./scripts \
	./oomoxify.sh \
		${pkgdir}/opt/oomox/oomoxify
cd ..


mkdir -p ${pkgdir}/usr/bin/
cp ./packaging/bin/* ${pkgdir}/usr/bin/

mkdir -p ${pkgdir}/usr/share/applications/
cp ./packaging/oomox.desktop ${pkgdir}/usr/share/applications/

exit 0
