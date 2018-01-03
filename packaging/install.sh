#!/usr/bin/env bash
set -ueo pipefail

# @TODO: mb rewrite it as a Makefile

srcdir=$(readlink -e $1)
pkgdir=$(readlink -e $2)

if [[ -d ${pkgdir}/opt/oomox ]] ; then
	rm -r ${pkgdir}/opt/oomox
fi
mkdir -p ${pkgdir}/opt/oomox

cd ${srcdir}
cp -prf \
	./CREDITS \
	./LICENSE \
	./README.md \
	./colors \
	./gui.sh \
	./oomox_gui \
	./plugins \
	./po \
	./po.mk \
		${pkgdir}/opt/oomox
rm -r ${pkgdir}/opt/oomox/plugins/theme_materia/materia-theme/.git*
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/.git*
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/.editorconfig
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/.*.yml
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/{D,d}ocker*
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/maintenance*
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/screenshot*
rm -r ${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/test*
rm -r ${pkgdir}/opt/oomox/plugins/icons_archdroid/archdroid-icon-theme/.git*
rm -r ${pkgdir}/opt/oomox/plugins/icons_gnomecolors/gnome-colors-icon-theme/.git*

mkdir ${pkgdir}/opt/oomox/oomoxify
cd ${srcdir}/oomoxify
cp -prf \
	./scripts \
	./oomoxify.sh \
		${pkgdir}/opt/oomox/oomoxify
cd ..

cd ${pkgdir}/opt/oomox/
# will update ./po and produce ./locale dir:
make -f po.mk install
rm ${pkgdir}/opt/oomox/po.mk

mkdir -p ${pkgdir}/usr/bin/
cp ${srcdir}/packaging/bin/* ${pkgdir}/usr/bin/

mkdir -p ${pkgdir}/usr/share/applications/
cp ${srcdir}/packaging/oomox.desktop ${pkgdir}/usr/share/applications/

exit 0
