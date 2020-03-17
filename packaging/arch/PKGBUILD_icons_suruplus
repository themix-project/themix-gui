# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/gusbemacbe/suru-plus/

_pkgname=themix-icons-suru-plus
_reponame=suru-plus
pkgname="${_pkgname}-git"
pkgver=30.0.r2.g9bd895f32
pkgrel=1
pkgdesc="Suru++ icons plugin for Themix GUI designer"
arch=('x86_64' 'i686')
url="https://github.com/gusbemacbe/suru-plus/"
license=('GPL3')
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
	"${_reponame}::git+https://github.com/gusbemacbe/suru-plus.git#branch=master"
)
md5sums=('SKIP'
         'SKIP')
depends=(
	'sed'
    'findutils'
)
makedepends=(
	'git'
	'python'
)
optdepends=(
	'themix-gui: GUI'
    'yaru-icon-theme: fallback icons'
    'gnome-icon-theme: fallback icons'
    'gnome-icon-theme-symbolic: fallback icons'
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
	git describe --tags --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g;s/^v//'
}

package() {
	_oomox_dir=/opt/oomox
	_plugin_name=icons_suruplus
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
