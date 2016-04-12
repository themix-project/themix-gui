# Maintainer: Yauhen Kirylau <yawghen AT gmail.com>
# Upstream URL: https://github.com/actionless/oomox

pkgname=oomox-git
pkgver=0.14.1
pkgrel=1
pkgdesc="Numix fork with color-changing script (GTK2, GTK3)"
arch=('x86_64' 'i686')
url="https://github.com/actionless/oomox"
license=('GPLv3')
source=(
	"git://github.com/actionless/oomox.git#branch=master"
)
md5sums=("SKIP")
depends=('bash' 'glib2' 'gdk-pixbuf2' 'ruby-sass' 'python-gobject')
optdepends=('xorg-xrdb: for the `xresources` theme')

pkgver() {
  cd oomox
  git describe | sed 's/^v//;s/-/./g'
}

package() {
	mkdir -p ${pkgdir}/opt/oomox
	mv ./oomox/* ${pkgdir}/opt/oomox
	mkdir -p ${pkgdir}/usr/bin/
	cat > ${pkgdir}/usr/bin/oomox-gui <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./gui.sh "$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-gui
	cat > ${pkgdir}/usr/bin/oomox-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./change_color.sh "$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-cli
}
