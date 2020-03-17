# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/themix-project/gnome-colors-icon-theme

_pkgname=themix-icons-gnome-colors
_reponame=gnome-colors-icon-theme
pkgname="${_pkgname}-git"
pkgver=5.5.5.r0.gcd8b05a
pkgrel=2
pkgdesc="Gnome-Colors icons plugin for Themix GUI designer"
arch=('x86_64' 'i686')
url="https://github.com/themix-project/gnome-colors-icon-theme"
license=('GPL3')
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
	"${_reponame}::git+https://github.com/themix-project/gnome-colors-icon-theme.git#branch=master"
)
md5sums=('SKIP'
         'SKIP')
depends=(
	'librsvg'
	'sed'
	'findutils'
	'grep'
	'bc'
	'imagemagick'
)
makedepends=(
	'git'
	'python'
)
optdepends=(
	'themix-gui: GUI'
	'gnome-icon-theme: fallback icons'
	'gnome-icon-theme-symbolic: fallback icons'
	'adwaita-icon-theme: fallback icons'
	'breeze-icons: fallback icons'
	'oxygen-icons: fallback icons'
)
options=(
	'!strip'
)
provides=($_pkgname)
conflicts=(
    $_pkgname
    'oomox'
    'oomox-git'
)

pkgver() {
	cd "${srcdir}/${_reponame}"
	git describe --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
	_oomox_dir=/opt/oomox
	_plugin_name=icons_gnomecolors
	_plugin_subpath="/${_reponame}"

	pkg_tmp_dir="${pkgdir}/_tmp"
	rm -fr "$pkg_tmp_dir"
	cp -r "${srcdir}/oomox" "$pkg_tmp_dir"
	rm -rf "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath}"
	cp -r "${srcdir}/${_reponame}" "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath}"

	cd "$pkg_tmp_dir"
	make DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" "install_${_plugin_name}"
	rm -fr "$pkg_tmp_dir"

	python -O -m compileall "${pkgdir}${_oomox_dir}/plugins/${_plugin_name}" -d "${_oomox_dir}/plugins/${_plugin_name}"
}

# vim: ft=PKGBUILD
