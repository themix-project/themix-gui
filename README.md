oomox theme designer
=====

Graphical application for generating different color variations of a Numix-based and Materia (ex-Flat-Plat) themes (GTK2, GTK3), Gnome-Colors and Archdroid icon themes.

<a href="https://aur.archlinux.org/packages/oomox"><img src="https://raw.githubusercontent.com/themix-project/oomox/flathub/packaging/download_aur.png" width="160"></a>
<a href="#ubuntu"><img src="https://raw.githubusercontent.com/themix-project/oomox/flathub/packaging/download_deb.png" width="160"></a>
<a href="https://copr.fedorainfracloud.org/coprs/tcg/themes/"><img src="https://raw.githubusercontent.com/themix-project/oomox/flathub/packaging/download_copr.png" width="160"></a>
<a href="https://flathub.org/apps/details/com.github.themix_project.Oomox"><img src="https://flathub.org/assets/badges/flathub-badge-en.png" width="160"></a>

Installation:
  * [Arch Linux, Manjaro](#arch-linux "")
  * [CentOS, Fedora, Mageia](#centos-fedora-mageia "")
  * [Slackware](#slackware "")
  * [Ubuntu](#ubuntu "")
  * [Other distributions](#other-distributions "")

Other topics:
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Spotify](#spotify "")
  * [Review videos/Usage instructions](#review-articles-and-videos "")


![Screenshot GUI](https://raw.githubusercontent.com/themix-project/oomox/master/screenshot_gui.png "Screenshot GUI")

![Screenshot image import](https://raw.githubusercontent.com/themix-project/oomox/master/screenshot_pil.png "Screenshot image import")

[Big screenshot with number of generated themes 🔗](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)

[Latest Oomox GTK theme screenshots 🔗](https://github.com/themix-project/oomox-gtk-theme/tree/master/screenshots)


### Arch Linux:

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


### Slackware

There is a slackbuild:
https://slackbuilds.org/repository/14.2/desktop/oomox/


### Ubuntu

For Ubuntu 17.04+ you can download `oomox.deb` package here:
https://github.com/themix-project/oomox/releases

```sh
sudo dpkg -i ./oomox.deb
sudo apt install -f
```


For older Ubuntu releases install the dependencies manually and next follow general installation instructions [below](#installation "").
 - [List of dependencies](https://github.com/themix-project/oomox/blob/master/packaging/ubuntu/control#L5)
 - [How to install `sassc>=3.4`](https://askubuntu.com/questions/849057/how-to-install-libsass-on-ubuntu-16-04)


### Other distributions:


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

Materia theme:
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
# if you need to generate French locale:
make -f po.mk install
```

#### Running

```sh
./gui.sh
```

After exporting a theme select the generated theme (oomox-YOUR-THEME-NAME) in your appearance config tool (for example, _lxappearance_ or _gnome-tweak-tool_).

If your prefer CLI interface, refer to `change_color.sh` scripts inside `./plugins/`.



#### Spotify:

Spotify theme can be also exported from GUI, but if you prefer commandline interface:

```sh
./plugins/oomoxify/oomoxify.sh ./colors/gnome-colors/shiki-noble
```

Also you can normalize font weight with `-w` argument, see `-h` for usage.

Spotify theme settings are backed up to `~/.config/oomox/spotify_backup`. To undo the changes made by oomoxify, these files can be copied back to their original location `/usr/share/spotify/Apps`. Spotify can also be reinstalled, which will reset these files as well.


### Using with tiling WMs:

To resolve borders/shadow problem in tiling window managers create/append to
`~/.config/gtk-3.0/gtk.css`:

```css
.window-frame, .window-frame:backdrop {
    box-shadow: 0 0 0 black;
    border-style: none;
    margin: 0;
    border-radius: 0;
}
.titlebar {
    border-radius: 0;
}
window decoration {
    margin: 0;
    border: 0;
}
```


### Review articles and videos

To learn more about using the application you can check these sources:

  * 2018, https://www.youtube.com/watch?v=XO9QA1njIOM by AddictiveTips
  * https://delightlylinux.wordpress.com/2016/08/22/customize-theme-colors-with-oomox/
  * 2016, https://www.youtube.com/watch?v=Dh5TuIYQ6jo by Spatry
  * http://www.webupd8.org/2016/05/easily-create-your-own-numix-based-gtk.html
  * http://www.webupd8.org/2016/06/tool-to-customize-numix-theme-colors.html
