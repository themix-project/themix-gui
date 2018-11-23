oomox theme designer
=====

Graphical application for generating different color variations of Oomox (Numix-based), Materia (ex-Flat-Plat) and Arc themes (GTK2, GTK3, Cinnamon, GNOME, Openbox, Xfwm), Gnome-Colors and Archdroid icon themes. Have a hack for HiDPI in gtk2.

<a href="https://aur.archlinux.org/packages/oomox"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_aur.png" width="160"></a>
<a href="#debian-ubuntu-linux-mint"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_deb.png" width="160"></a>
<a href="https://copr.fedorainfracloud.org/coprs/tcg/themes/"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_copr.png" width="160"></a>
<a href="https://slackbuilds.org/repository/14.2/desktop/oomox/"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_slackware.png" width="54"></a>
<a href="https://github.com/void-linux/void-packages/tree/master/srcpkgs/oomox"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_void.png" width="54"></a>
<a href="https://flathub.org/apps/details/com.github.themix_project.Oomox"><img src="https://flathub.org/assets/badges/flathub-badge-en.png" width="160"></a>


Table of contents:
  * [Installing with package manager](#installation "")
  * [Installing manually](#other-distributions "")
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Spotify](#spotify "")
  * [Review videos/Usage instructions](#review-articles-and-videos "")


![Screenshot GUI](https://raw.githubusercontent.com/themix-project/oomox/master/screenshot_gui.png "Screenshot GUI")

![Screenshot image import](https://raw.githubusercontent.com/themix-project/oomox/master/screenshot_pil.png "Screenshot image import")

[Big screenshot with number of generated themes 🔗](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)

[Latest Oomox GTK theme screenshots 🔗](https://github.com/themix-project/oomox-gtk-theme/tree/master/screenshots)



## Installation



### Arch Linux

#### Install

```
pikaur -S oomox-git
```

AUR helpers are [not officialy supported](https://wiki.archlinux.org/index.php/AUR_helpers), so you can also [install it manually](https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_packages) from either [rolling-release](https://aur.archlinux.org/packages/oomox-git/) or [stable](https://aur.archlinux.org/packages/oomox/) PKGBUILD.

#### Open the GUI

```
oomox-gui
```



### CentOS, Fedora, Mageia

Oomox can be installed by using a third party COPR repository:
```bash
sudo dnf copr enable tcg/themes
sudo dnf install oomox
```



### Debian, Ubuntu, Linux Mint

For Debian 9+, Ubuntu 17.04+ or Linux Mint 19+ you can download `oomox.deb` package here:
https://github.com/themix-project/oomox/releases

```sh
sudo dpkg -i ./oomox.deb
sudo apt install -f
```

Or, if you don't want to install third-party binary package you can build it on your own:

```sh
# with docker:
sudo systemctl start docker
sudo ./packaging/ubuntu/docker_ubuntu_package.sh  # sudo is not needed if your user is in docker group

# or directly from ubuntu host if you don't like docker:
./packaging/ubuntu/create_ubuntu_package.sh
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
 - `xorg-xrdb` - optional, for xresources themes

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

Materia and Arc themes:
 - `sassc>=3.4`
 - `glib-compile-schemas` from `glib2`
 - `gdk-pixbuf2`
 - `bc`
 - `sed`
 - `find`
 - `grep`
 - `optipng`
 - `parallel`
 - `inkscape`
 - `gtk2-engine-murrine`

Gnome-Colors icons:
 - `bc`
 - `sed`
 - `find`
 - `grep`
 - `rsvg-convert` from `librsvg`
 - `imagemagick`
 - `breeze-icons` - optional, to provide more fallbacks

Archdroid icons:
 - `sed`
 - `find`
 - `breeze-icons` - optional, to provide more fallbacks

Spotify theme:
 - `polkit` or `gksu`
 - `zip`
 - `bc`
 - `grep`

Import colors from images:
 - `python3 PIL or Pillow`

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


### Review articles and videos

To learn more about using the application you can check these sources:

  * 2018, https://www.youtube.com/watch?v=XO9QA1njIOM by AddictiveTips
  * https://delightlylinux.wordpress.com/2016/08/22/customize-theme-colors-with-oomox/
  * 2016, https://www.youtube.com/watch?v=Dh5TuIYQ6jo by Spatry
  * http://www.webupd8.org/2016/05/easily-create-your-own-numix-based-gtk.html
  * http://www.webupd8.org/2016/06/tool-to-customize-numix-theme-colors.html
