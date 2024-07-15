Manual Installation in Unsupported Distros
==========================================

#### Prerequisites

For GUI app itself:
 - `python3>=3.10`
 - `gtk3>=3.18`
 - `python3-gobject`
 - `gdk-pixbuf2`

##### For plugins:

Oomox theme:
 - `sassc>=3.4`
 - `rsvg-convert` from `librsvg`
 - `glib-compile-schemas` from `glib2`
 - `gdk-pixbuf2`
 - `bc`
 - `sed`
 - `find`
 - `grep`

Materia theme (deprecated):
 - `sassc>=3.4`
 - `glib-compile-schemas` from `glib2`
 - `gdk-pixbuf2`
 - `sed`
 - `find`
 - `grep`
 - `optipng`
 - `gtk2-engine-murrine`
 - `inkscape` (or `resvg`, but it's currently disabled)
 - `parallel`
 - `meson`

Gnome-Colors icons:
 - `bc`
 - `sed`
 - `find`
 - `grep`
 - `rsvg-convert` from `librsvg`
 - `imagemagick`
 - `breeze-icons` - optional, to provide more fallbacks

Archdroid, Papirus and Suru++ icons:
 - `sed`
 - `find`
 - `breeze-icons` - optional for Archdroid, to provide more fallbacks

Spotify theme:
 - `polkit` or `gksu`
 - `zip`
 - `bc`
 - `grep`

Import colors from images:
 - `python3 PIL or Pillow`
 - `python3 colorz` - optional, extra image analyzer
 - `python3 colorthief` - optional, extra image analyzer
 - `python3 haishoku` - optional, extra image analyzer

Base16 format support:
 - `python3 pystache`
 - `python3 yaml`

Xresources import:
 - `xorg-xrdb` - optional, for xresources themes


#### Installation

```sh
git clone https://github.com/themix-project/oomox.git --recursive
cd oomox
# if you need to generate locales:
make -f po.mk install
```

#### Running

```sh
./gui.sh
```

After exporting a theme select the generated theme (oomox-YOUR-THEME-NAME) in your appearance config tool (for example, `lxappearance` or `gnome-tweak-tool`).
