# Maintainer: Yauhen Kirylau <yawghen AT gmail.com>
# Upstream URL: https://github.com/themix-project/oomox

pkgname=oomox-git
pkgver=1.9.0.1
pkgrel=1
pkgdesc="Graphical application for generating different color variations
of Oomox(Numix-based), Materia (ex-Flat-Plat) and Arc themes
(GTK2, GTK3, Cinnamon, GNOME, Openbox, Xfwm),
gnome-colors and ArchDroid icon themes.
Have a hack for HiDPI in gtk2."
arch=('x86_64' 'i686')
url="https://github.com/themix-project/oomox"
license=('GPL3')
	#"git+https://github.com/NicoHood/arc-theme.git#branch=master"
source=(
	"git+https://github.com/themix-project/oomox.git#branch=master"
	"git+https://github.com/themix-project/oomox-gtk-theme.git#branch=master"
	"git+https://github.com/nana-4/materia-theme.git#branch=master"
	"git+https://github.com/actionless/arc-theme.git#branch=resvg"
	"git+https://github.com/themix-project/archdroid-icon-theme.git#branch=master"
	"git+https://github.com/themix-project/gnome-colors-icon-theme.git#branch=master"
	"git+https://github.com/themix-project/oomoxify.git#branch=master"
	"git+https://github.com/base16-builder/base16-builder#branch=master"
	"git+https://github.com/numixproject/numix-icon-theme.git#branch=master"
	"git+https://github.com/numixproject/numix-folders.git#branch=master"
)
md5sums=(
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
)
depends=(
	'gtk3'
	'python-gobject'
	'glib2'  # oomox, materia, arc
	'gdk-pixbuf2'  # oomox, materia, arc
	'gtk-engine-murrine'  # oomox, materia, arc
	'gtk-engines'  # oomox, materia, arc
	'gnome-themes-extra'  # materia
	'sassc'  # oomox, materia, arc
	'librsvg'  # oomox, gnome-colors
	'sed'  # oomox, materia, arc, gnome-colors, archdroid
	'findutils'  # oomox, materia, arc, gnome-colors, arch-droid
	'grep'  # oomoxify, oomox, materia, arc, gnome-colors
	'bc'  # oomoxify, oomox, materia, arc, gnome-colors
	'zip'  # oomoxify
	'polkit'  # oomoxify
	'imagemagick'  # gnome-colors
	'parallel'  # materia, arc
	'optipng'  # materia, arc
	'python-pillow'  # import_pil

	'resvg-git'  # materia, arc
	##or
	#'inkscape'  # materia, arc
)
makedepends=(
	'git'
)
optdepends=(
	'xorg-xrdb: for the `xresources` theme'
	'breeze-icons: more fallback icons'
	'gksu: for applying Spotify theme from GUI without polkit'
	'colorz: additional image analyzer for "Import colors from image" plugin'
	'python-colorthief: additional image analyzer for "Import colors from image" plugin'
	'python-haishoku: additional image analyzer for "Import colors from image" plugin'
)
options=(
	'!strip'
)

pkgver() {
	cd "${srcdir}/oomox"
	git describe --long | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}

prepare(){
	cd "${srcdir}/oomox"
	git submodule init
	git config submodule.gtk-theme.url $srcdir/oomox-gtk-theme
	git config submodule.materia-theme.url $srcdir/materia-theme
	git config submodule.arc-theme.url $srcdir/arc-theme
	git config submodule.archdroid-icon-theme.url $srcdir/archdroid-icon-theme
	git config submodule.gnome-colors-icon-theme.url $srcdir/gnome-colors-icon-theme
	git config submodule.oomoxify.url $srcdir/oomoxify
	git config submodule.base16-builder.url $srcdir/base16-builder
	git config submodule.numix-folders.url $srcdir/numix-folders
	git config submodule.numix-icon-theme.url $srcdir/numix-icon-theme
	git submodule update
}

package() {
	_oomox_dir=/opt/oomox
	_oomox_gui_dir=${_oomox_dir}/oomox_gui

	cd "${srcdir}/oomox"
	make DESTDIR="${pkgdir}" APPDIR="${_oomox_dir}" PREFIX="/usr" install
	python -O -m compileall ${pkgdir}${_oomox_gui_dir} -d ${_oomox_gui_dir}
}
