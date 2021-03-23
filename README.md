Themix GUI theme designer
=====

[![Build Status](https://travis-ci.com/themix-project/oomox.svg?branch=master)](https://travis-ci.org/themix-project/oomox)

Graphical application for generating different color variations of Oomox (Numix-based) and Materia (ex-Flat-Plat) themes (GTK2, GTK3, Cinnamon, GNOME, Openbox, Xfwm), Archdroid, Gnome-Color, Numix, Papirus and Suru++ icon themes. Have a hack for HiDPI in gtk2.

<a href="https://aur.archlinux.org/packages/themix-full-git"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_aur.png" height="54"></a>
<a href="#debian-ubuntu-linux-mint"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_deb.png" height="54"></a>
<a href="https://slackbuilds.org/repository/14.2/desktop/oomox/"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_slackware.png" height="54"></a>
<a href="https://flathub.org/apps/details/com.github.themix_project.Oomox"><img src="https://flathub.org/assets/badges/flathub-badge-en.png" height="54"></a>


Table of contents:
  * [Installing with package manager](#installation "")
  * [Installing manually](#other-distributions "")
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Extra GTK3 CSS hacks](#extra-gtk3-css-hacks "")
  * [Spotify](#spotify "")
  * [Review videos/Usage instructions](#review-articles-and-videos "")

![Screenshot image import](https://raw.githubusercontent.com/themix-project/oomox/master/screenshots/pokedex_dawn.png "Screenshot image import")

![Screenshot GUI](https://raw.githubusercontent.com/themix-project/oomox/master/screenshots/screenshot_gui.png "Screenshot GUI")

[Big screenshot with number of generated themes 🔗](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)

[Latest Oomox GTK theme screenshots 🔗](https://github.com/themix-project/oomox-gtk-theme/tree/master/screenshots)



## Installation



### Arch Linux

#### Install

```
pikaur -S themix-full-git
```

AUR helpers are [not officially supported](https://wiki.archlinux.org/index.php/AUR_helpers), so you can also [install it manually](https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_packages) from either [rolling-release](https://aur.archlinux.org/packages/themix-full-git/) or [stable](https://aur.archlinux.org/packages/oomox/) PKGBUILD.

#### Open the GUI

```
oomox-gui
```



### Debian, Ubuntu, Linux Mint

For Debian 9+, Ubuntu 17.04+ or Linux Mint 19+ you can download `oomox.deb` package here:
https://github.com/themix-project/oomox/releases
Make sure what `universe` repository is enabled.

```sh
sudo apt install ./oomox_VERSION_17.04+.deb  # or ./oomox_VERSION_18.10+.deb for Ubuntu 18.10+
```

Or, if you don't want to install third-party binary package you can build it on your own:

```sh
# with docker:
sudo systemctl start docker
sudo ./packaging/ubuntu/docker_ubuntu_package.sh  # sudo is not needed if your user is in docker group

# or directly from ubuntu host if you don't like docker:
./packaging/ubuntu/create_ubuntu_package.sh control
# or ./packaging/ubuntu/create_ubuntu_package.sh control_1810
```


For older releases install the dependencies manually and next follow general installation instructions [below](#installation-1 "").
 - [List of dependencies](https://github.com/themix-project/oomox/blob/master/packaging/ubuntu/control#L5)
 - [How to install `sassc>=3.4`](https://askubuntu.com/questions/849057/how-to-install-libsass-on-ubuntu-16-04)



### Other distributions


#### Prerequisites

For GUI app itself:
 - `python3-gobject`
 - `gtk3>=3.18`
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

Materia theme:
 - `sassc>=3.4`
 - `glib-compile-schemas` from `glib2`
 - `gdk-pixbuf2`
 - `sed`
 - `find`
 - `grep`
 - `optipng`
 - `gtk2-engine-murrine`
 - `resvg` or `inkscape`
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

After exporting a theme select the generated theme (oomox-YOUR-THEME-NAME) in your appearance config tool (for example, _lxappearance_ or _gnome-tweak-tool_).


### CLI

If your prefer CLI interface, refer to `change_color.sh` scripts inside `./plugins/`. For `xresources` and `random` themes in CLI use palettes from `/opt/oomox/scripted_colors/` directory. Using scripted palettes enables you to use bash to write simple generators for dynamic themes (as alternative to plugins in oomox-gui). GUI is not attempting to execute any scripted palettes with bash because downloading such scripted themes from random places could lead to unexpected result so you can use them only with CLI, when you really know what you're doing.



#### Spotify:

Spotify theme can be also exported from GUI, but if you prefer commandline interface:

```sh
./plugins/oomoxify/oomoxify.sh ./colors/gnome-colors/shiki-noble
```

Also you can normalize font weight with `-w` argument, see `-h` for usage.

Spotify theme settings are backed up to `~/.config/oomox/spotify_backup`. To undo the changes made by oomoxify, these files can be copied back to their original location `/usr/share/spotify/Apps`. Spotify can also be reinstalled, which will reset these files as well.

Users running Spotify under Flatpak should set their "Spotify path" in oomox to `/var/lib/flatpak/app/com.spotify.Client/current/active/files/extra/share/spotify/Apps` in order to apply the theme.


### Using with tiling WMs

Create/append to `~/.config/gtk-3.0/gtk.css`:

```css
/* remove window title from Client-Side Decorations */
.solid-csd headerbar .title {
    font-size: 0;
}

/* hide extra window decorations/double border */
window decoration {
    margin: 0;
    border: none;
    padding: 0;
}
```


### Extra GTK3 CSS hacks

Create/append to `~/.config/gtk-3.0/gtk.css`:

```css
* {
  text-shadow: none;
}
```


### Review articles and videos

To learn more about using the application you can check these sources:

  * 2019, [Customizing icon themes animated tutorial](https://github.com/themix-project/oomox/wiki/Customizing-icon-themes)
  * 2019, [How to contribute your theme from Github website](https://github.com/themix-project/oomox/wiki/How-to-contribute-your-theme-from-Github-website)
  * 2019, [How to import and export Base16 themes in Themix/Oomox](https://github.com/themix-project/oomox/wiki/How-to-import-and-export-Base16-themes-in-Themix-Oomox)
  * 2018, https://www.youtube.com/watch?v=XO9QA1njIOM by AddictiveTips
  * https://delightlylinux.wordpress.com/2016/08/22/customize-theme-colors-with-oomox/
  * 2016, https://www.youtube.com/watch?v=Dh5TuIYQ6jo by Spatry
  * http://www.webupd8.org/2016/05/easily-create-your-own-numix-based-gtk.html
  * http://www.webupd8.org/2016/06/tool-to-customize-numix-theme-colors.html
