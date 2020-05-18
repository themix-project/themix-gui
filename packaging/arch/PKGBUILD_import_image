# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/themix-project/oomox

_pkgname=themix-import-images
pkgname="${_pkgname}-git"
pkgver=1.13.3
pkgrel=1
pkgdesc="Import plugin for Themix GUI designer to get color palettes from the images"
arch=('x86_64' 'i686')
url="https://github.com/themix-project/oomox"
license=('GPL3')
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
)
md5sums=('SKIP')
depends=(
	'themix-gui'
	'python-pillow'
)
makedepends=(
	'git'
)
optdepends=(
	'colorz: additional image analyzer'
	'python-colorthief: additional image analyzer'
	'python-haishoku: additional image analyzer'
)
provides=($_pkgname)
conflicts=(
    $_pkgname
    'oomox'
    'oomox-git'
)

pkgver() {
	cd "${srcdir}/oomox"
	git describe --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
	_oomox_dir=/opt/oomox
	_plugin_name=import_pil

	cd "${srcdir}/oomox"
	make DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" install_import_images
	python -O -m compileall "${pkgdir}${_oomox_dir}/plugins/${_plugin_name}" -d "${_oomox_dir}/plugins/${_plugin_name}"
}

# vim: ft=PKGBUILD
