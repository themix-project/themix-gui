# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/numixproject/numix-icon-theme

_pkgname=themix-icons-numix
_reponame1=numix-icon-theme
_reponame2=numix-folders
pkgname="${_pkgname}-git"
pkgver=20.06.07.r8.g91e4a9747
pkgrel=1
pkgdesc="Numix icons plugin for Themix GUI designer"
arch=('x86_64' 'i686')
url="https://github.com/numixproject/numix-icon-theme"
license=('GPL3')
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
	"${_reponame1}::git+https://github.com/numixproject/numix-icon-theme.git#branch=master"
	"${_reponame2}::git+https://github.com/numixproject/numix-folders.git#branch=master"
)
md5sums=('SKIP'
         'SKIP'
         'SKIP')
depends=(
	'sed'
    'findutils'
    'bc'
)
makedepends=(
	'git'
	'python'
)
optdepends=(
	'themix-gui: GUI'
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
	cd "${srcdir}/${_reponame1}"
	git describe --tags --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
	_oomox_dir=/opt/oomox
	_plugin_name=icons_numix
	_plugin_subpath1="/${_reponame1}"
	_plugin_subpath2="/${_reponame2}"

	pkg_tmp_dir="${pkgdir}/_tmp"
	rm -fr "$pkg_tmp_dir"
	cp -r "${srcdir}/oomox" "$pkg_tmp_dir"
	rm -rf "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath1}"
	cp -r "${srcdir}/${_reponame1}" "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath1}"
	rm -rf "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath2}"
	cp -r "${srcdir}/${_reponame2}" "${pkg_tmp_dir}/plugins/${_plugin_name}${_plugin_subpath2}"

	cd "$pkg_tmp_dir"
	make DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" "install_${_plugin_name}"
	rm -fr "$pkg_tmp_dir"

	python -O -m compileall "${pkgdir}${_oomox_dir}/plugins/${_plugin_name}" -d "${_oomox_dir}/plugins/${_plugin_name}"
}

# vim: ft=PKGBUILD
