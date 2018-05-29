#!/usr/bin/env bash
#set -x
set -ueo pipefail

# @TODO: mb rewrite it as a Makefile

srcdir=$(readlink -e "$1")
#pkgdir=$(readlink -e "$2")
pkgdir="${2}"

if [[ -d "${pkgdir}/opt/oomox" ]] ; then
	rm -r "${pkgdir}/opt/oomox"
fi
mkdir -p "${pkgdir}/opt/oomox"

cd "${srcdir}"
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
	./terminal_templates \
		"${pkgdir}/opt/oomox"
rm -rf "${pkgdir}/opt/oomox/plugins/oomoxify/".git*
rm -rf "${pkgdir}/opt/oomox/plugins"/*/*/.git*
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/".editorconfig
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/".*.yml
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/"{D,d}ocker*
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/"maintenance*
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/"screenshot*
rm -rf "${pkgdir}/opt/oomox/plugins/theme_oomox/gtk-theme/"test*

cd "${pkgdir}/opt/oomox/"
# will update ./po and produce ./locale dir:
make -f po.mk install
rm "${pkgdir}/opt/oomox/po.mk"

install -Dp -m 755 --target-directory="${pkgdir}/usr/bin/" "${srcdir}/packaging/bin/"*

install -d "${pkgdir}/usr/share/applications/"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox.desktop" "${pkgdir}/usr/share/applications/"

install -d "${pkgdir}/usr/share/appdata/"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox.appdata.xml" "${pkgdir}/usr/share/appdata/"

#install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox.svg" "${pkgdir}/usr/share/icons/hicolor/scalable/apps/com.github.themix-project.oomox.svg"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-symbolic.svg" "${pkgdir}/usr/share/icons/hicolor/symbolic/apps/com.github.themix-project.oomox.svg"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-16.png" "${pkgdir}/usr/share/icons/hicolor/16x16/apps/com.github.themix-project.oomox.png"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-24.png" "${pkgdir}/usr/share/icons/hicolor/24x24/apps/com.github.themix-project.oomox.png"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-32.png" "${pkgdir}/usr/share/icons/hicolor/32x32/apps/com.github.themix-project.oomox.png"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-48.png"  "${pkgdir}/usr/share/icons/hicolor/48x48/apps/com.github.themix-project.oomox.png"
install -Dp -m 644 "${srcdir}/packaging/com.github.themix-project.oomox-512.png" "${pkgdir}/usr/share/icons/hicolor/512x512/apps/com.github.themix-project.oomox.png"

exit 0
