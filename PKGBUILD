# Maintainer: Yauhen Kirylau <yawghen AT gmail.com>
# Upstream URL: https://github.com/actionless/oomox

pkgname=oomox-git
pkgver=1.4.4
pkgrel=1
pkgdesc="Graphical application for generating different color variations
of Numix and Materia (ex-Flat-Plat) themes (GTK2, GTK3),
gnome-colors and ArchDroid icon themes.
Have a hack for HiDPI in gtk2."
arch=('x86_64' 'i686')
url="https://github.com/actionless/oomox"
license=('GPLv3')
source=(
	"git+https://github.com/actionless/oomox.git#branch=master"
	"git+https://github.com/actionless/oomox-gtk-theme.git#branch=master"
	"git+https://github.com/nana-4/materia-theme.git#branch=master"
	"git+https://github.com/actionless/oomox-archdroid-icon-theme.git#branch=master"
	"git+https://github.com/actionless/oomox-gnome-colors-icon-theme.git#branch=master"
	"git+https://github.com/actionless/oomoxify.git#branch=master"
)
md5sums=(
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
	"SKIP"
)
depends=(
	'coreutils'
	'bash'
	'grep'
	'sed'
	'bc'
	'zip'
	'glib2'
	'gdk-pixbuf2'
	'sassc'
	'python-gobject'
	'gtk-engine-murrine'
	'gtk-engines'
	'polkit'
	'parallel'
	'optipng'
	'inkscape'
	'imagemagick'
)
makedepends=(
	'git'
)
optdepends=(
	'xorg-xrdb: for the `xresources` theme'
	'breeze-icons: more fallback icons'
	'gksu: for applying Spotify theme from GUI without polkit'
)
options=(
	'!strip'
)

pkgver() {
	cd oomox
	git describe | sed 's/^v//;s/-/+/g'
}

prepare(){
	cd "${srcdir}/oomox"
	git submodule init
	git config submodule.gtk-theme.url $srcdir/oomox-gtk-theme
	git config submodule.materia-theme.url $srcdir/materia-theme
	git config submodule.archdroid-icon-theme.url $srcdir/oomox-archdroid-icon-theme
	git config submodule.gnome-colors-icon-theme.url $srcdir/oomox-gnome-colors-icon-theme
	git config submodule.oomoxify.url $srcdir/oomoxify
	git submodule update
}

package() {
	mkdir -p ${pkgdir}/opt/oomox
	cd ./oomox
	make -f po.mk install

	cp -prf \
		./CREDITS \
		./LICENSE \
		./README.md \
		./colors \
		./gui.sh \
		./locale \
		./oomox_gui \
		./po \
			${pkgdir}/opt/oomox

	mkdir ${pkgdir}/opt/oomox/gtk-theme
	cd ./gtk-theme
	cp -prf \
		./CHANGES \
		./CREDITS \
		./LICENSE \
		./Makefile \
		./README.md \
		./change_color.sh \
		./scripts \
		./src \
			${pkgdir}/opt/oomox/gtk-theme
	cd ..

	mkdir ${pkgdir}/opt/oomox/materia-theme
	cd ./materia-theme
	cp -prf \
		./COPYING \
		./HACKING.md \
		./README.md \
		./change_color.sh \
		./install.sh \
		./parse-sass.sh \
		./scripts \
		./src \
			${pkgdir}/opt/oomox/materia-theme
	cd ..

	mkdir ${pkgdir}/opt/oomox/archdroid-icon-theme
	cd ./archdroid-icon-theme
	cp -prf \
		./archdroid-icon-theme \
		./LICENSE \
		./README.md \
		./change_color.sh \
		./copyright \
			${pkgdir}/opt/oomox/archdroid-icon-theme
	cd ..

	mkdir ${pkgdir}/opt/oomox/gnome-colors-icon-theme
	cd ./gnome-colors-icon-theme
	cp -prf \
		./gnome-colors \
		./README.md \
		./change_color.sh \
			${pkgdir}/opt/oomox/gnome-colors-icon-theme
	cd ..

	mkdir ${pkgdir}/opt/oomox/oomoxify
	cd ./oomoxify
	cp -prf \
		./scripts \
		./oomoxify.sh \
			${pkgdir}/opt/oomox/oomoxify

	python -O -m compileall ${pkgdir}/opt/oomox/oomox_gui
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
exec ./gtk-theme/change_color.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-cli


	cat > ${pkgdir}/usr/bin/oomox-materia-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./materia-theme/change_color.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-materia-cli


	cat > ${pkgdir}/usr/bin/oomox-gnome-colors-icons-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./gnome-colors-icon-theme/change_color.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-gnome-colors-icons-cli


	cat > ${pkgdir}/usr/bin/oomox-archdroid-icons-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./archdroid-icon-theme/change_color.sh "\$@"
EOF
	chmod +x ${pkgdir}/usr/bin/oomox-archdroid-icons-cli


	cat > ${pkgdir}/usr/bin/oomoxify-cli <<EOF
#!/bin/sh
cd /opt/oomox/
exec ./oomoxify/oomoxify.sh "\$@"
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
