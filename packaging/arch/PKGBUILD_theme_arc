# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/arc-design/arc-theme/

_pkgname=themix-theme-arc
_reponame=arc-theme
pkgname="${_pkgname}-git"
pkgver=20190917.r3.g53e6188
pkgrel=1
pkgdesc="Arc theme plugin
 (GTK2, GTK3, Cinnamon, GNOME Shell, Metacity, Openbox, Unity, Xfwm) for Themix GUI designer."
arch=('x86_64' 'i686')
url="https://github.com/arc-design/arc-theme/"
license=('GPL3')
source=(
       "git+https://github.com/themix-project/oomox.git#branch=master"
       "${_reponame}::git+https://github.com/arc-design/arc-theme.git#branch=master"
)
md5sums=('SKIP'
         'SKIP')
depends=(
	'glib2'
	'gdk-pixbuf2'
	'gtk-engine-murrine'
	'gtk-engines'
	'sassc'
	'sed'
	'findutils'
	'grep'
	'bc'
	'optipng'

	'resvg'
	##or
	#'inkscape'
)
makedepends=(
       'git'
       'python'
)
optdepends=(
       'themix-gui: GUI'
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
       _plugin_name=theme_arc
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
