# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/nana-4/materia-theme/

_pkgname=themix-theme-materia
_reponame=materia-theme
pkgname="${_pkgname}-git"
pkgver=20210322.r6.g822e77e6
pkgrel=1
pkgdesc="Materia theme plugin
 (GTK2, GTK3, GTK4, Cinnamon, GNOME, Metacity, Unity, Xfwm) for Themix GUI designer.
 Have a hack for HiDPI in GTK2."
arch=('x86_64' 'i686')
url="https://github.com/nana-4/materia-theme"
license=('GPL3')
source=(
       "git+https://github.com/themix-project/oomox.git#branch=master"
       "${_reponame}::git+https://github.com/nana-4/materia-theme.git#branch=master"
)
md5sums=('SKIP'
         'SKIP')
depends=(
	'gtk3'
	'glib2'
	'gdk-pixbuf2'
	'gtk-engine-murrine'
	'gtk-engines'
	'gnome-themes-extra'
	'sassc'
	'sed'
	'findutils'
	'grep'
	'parallel'
	'meson'
	'optipng'

	'inkscape'
	## or
	#'resvg'
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
       _plugin_name=theme_materia
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
