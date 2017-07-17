# Maintainer: Yauhen Kirylau <yawghen AT gmail.com>
# Upstream URL: https://github.com/actionless/oomox

pkgname=oomox-git
pkgver=1.2.7
pkgrel=1
pkgdesc="Graphical application for generating different color variations
of Numix theme (GTK2, GTK3), gnome-colors and ArchDroid icon themes.
Have a hack for HiDPI in gtk2."
arch=('x86_64' 'i686')
url="https://github.com/actionless/oomox"
license=('GPLv3')
source=(
	"git+https://github.com/actionless/oomox.git#branch=master"
)
md5sums=("SKIP")
depends=(
	'bash'
	'bc'
	'zip'
	'glib2'
	'gdk-pixbuf2'
	'sassc'
	'python-gobject'
	'gtk-engine-murrine'
	'gtk-engines'
	'procps-ng'
	'polkit'
)
optdepends=(
	'xorg-xrdb: for the `xresources` theme'
	'imagemagick: for icon theme generation'
	'inkscape: for icon theme generation'
	'gnome-colors-common-icon-theme: for using the generated icon theme'
	'breeze-icons: more fallback icons'
	'gksu: for applying Spotify theme from GUI without polkit'
	#'gnome-colors-icon-theme: for using the generated icon theme'  it's broken ATM
)

pkgver() {
  cd oomox
  git describe | sed 's/^v//;s/-/./g'
}

package() {
	make -C oomox -f po.mk install
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


	cat > ${pkgdir}/usr/bin/oomox-gnome-colors-icons-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./gnome-colors.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-gnome-colors-icons-cli


	cat > ${pkgdir}/usr/bin/oomox-archdroid-icons-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./archdroid.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-archdroid-icons-cli


	cat > ${pkgdir}/usr/bin/oomoxify-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./oomoxify.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomoxify-cli


	cat > ${pkgdir}/usr/share/applications/oomox.desktop <<EOF
[Desktop Entry]
Name=Oomox: customize icons and GTK themes
GenericName=Oomox
Comment=Graphical application for generating different color variations of Numix theme (GTK2, GTK3), gnome-colors and ArchDroid icon themes
Exec=oomox-gui
Terminal=false
Type=Application
Icon=preferences-desktop-theme
Categories=GNOME;GTK;Settings;DesktopSettings;X-XFCE-SettingsDialog;X-XFCE-PersonalSettings;
Keywords=color;gtk;highlight;theme;widget;numix;
StartupWMClass=oomox
X-GNOME-Gettext-Domain=oomox
X-Desktop-File-Install-Version=0.22
EOF

}
