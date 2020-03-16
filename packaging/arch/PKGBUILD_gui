# Maintainer: Yauhen Kirylau <actionless DOT loveless PLUS aur AT gmail MF com>
# Upstream URL: https://github.com/themix-project/oomox

pkgname=themix-gui-git
pkgver=1.12.6.r11.gf461833e
pkgrel=1
pkgdesc="Plugin-based theme designer GUI for
 environments (like GTK2, GTK3, Cinnamon, GNOME, MATE, Openbox, Xfwm),
 icons and terminal palettes."
arch=('x86_64' 'i686')
url="https://github.com/themix-project/oomox"
license=('GPL3')
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
)
md5sums=('SKIP')
depends=(
	'gtk3'
	'python-gobject'
)
makedepends=(
	'git'
)
optdepends=(
	'themix-icons-gnome-colors: Icons Style plugin'
	'themix-theme-materia: Theme Style plugin'
	'themix-theme-oomox: Theme Style plugin'
	'xorg-xrdb: for the `xresources` theme'
)
provides=('themix-gui')
conflicts=('themix-gui')

pkgver() {
	cd "${srcdir}/oomox"
	git describe --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
	_oomox_dir=/opt/oomox
	_oomox_gui_dir=${_oomox_dir}/oomox_gui

	cd "${srcdir}/oomox"
	make DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" install_gui
	python -O -m compileall ${pkgdir}${_oomox_gui_dir} -d ${_oomox_gui_dir}
}

# vim: ft=PKGBUILD
