# Maintainer: Yauhen Kirylau <yawghen AT gmail.com>
# Upstream URL: https://github.com/actionless/oomox

pkgname=oomox-git
pkgver=0.19.0
pkgrel=3
pkgdesc="Graphical application for generating different color variations 
of Numix theme (GTK2, GTK3) and gnome-colors icon theme"
arch=('x86_64' 'i686')
url="https://github.com/actionless/oomox"
license=('GPLv3')
source=(
	"git://github.com/actionless/oomox.git#branch=master"
)
md5sums=("SKIP")
depends=(
	'bash'
	'glib2'
	'gdk-pixbuf2'
	'ruby-sass'
	'python-gobject'
	'gtk-engine-murrine'
	'gtk-engines'
)
optdepends=(
	'xorg-xrdb: for the `xresources` theme'
	'imagemagick: for icon theme generation'
	'inkscape: for icon theme generation'
)

pkgver() {
  cd oomox
  git describe | sed 's/^v//;s/-/./g'
}

package() {
	mkdir -p ${pkgdir}/opt/oomox
	mv ./oomox/* ${pkgdir}/opt/oomox
	mkdir -p ${pkgdir}/usr/bin/
	mkdir -p ${pkgdir}/usr/share/applications/


	cat > ${pkgdir}/usr/bin/oomox-gui <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./gui.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-gui


	cat > ${pkgdir}/usr/bin/oomox-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./change_color.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-cli


	cat > ${pkgdir}/usr/bin/oomox-icons-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./gnome-colors.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-icons-cli


	cat > ${pkgdir}/usr/bin/oomoxify-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./oomoxify.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomoxify-cli


	cat > ${pkgdir}/usr/share/applications/oomox.desktop <<EOF
[Desktop Entry]
Name=Oomox
GenericName=Oomox
Comment=Graphical application for generating different color variations of Numix theme (GTK2, GTK3) and gnome-colors icon theme
Exec=oomox-gui
Terminal=false
Type=Application
Icon=preferences-desktop-theme
Categories=GNOME;GTK;Settings;DesktopSettings;X-XFCE-SettingsDialog;X-XFCE-PersonalSettings;
Keywords=color;gtk;highlight;theme;widget;numix;
StartupWMClass=__main__.py
X-GNOME-Gettext-Domain=oomox
X-Desktop-File-Install-Version=0.22
EOF

}
