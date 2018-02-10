oomox theme designer
=====

Graphical application for generating different color variations of a Numix-based and Materia (ex-Flat-Plat) themes (GTK2, GTK3), Gnome-Colors and Archdroid icon themes.

Installation:
  * [Arch Linux, Manjaro](#arch-linux "")
  * [CentOS, Fedora, Mageia](#centos-fedora-mageia "")
  * [Slackware](#slackware "")
  * [Ubuntu](#ubuntu "")
  * [Other distributions](#other-distributions "")
 
Other topics:
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Spotify](#spotify "")
  * [Review articles/Usage instructions](#review-articles "")
  * [Demo video](#demo-video "")


![Screenshot GUI](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui.png "Screenshot GUI")

[Big screenshot with number of generated themes 🔗](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)

[Latest Oomox GTK theme screenshots 🔗](https://github.com/actionless/oomox-gtk-theme/tree/master/screenshots)


### Arch Linux:

#### Install

```
pikaur -S oomox-git
```

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
https://github.com/actionless/oomox/releases

```sh
sudo dpkg -i ./oomox.deb
sudo apt install -f
```


For older Ubuntu releases install the dependencies manually and next follow general installation instructions [below](#installation "").
 - [List of dependencies](https://github.com/actionless/oomox/blob/master/packaging/ubuntu/control#L5)
 - [How to install `sassc>=3.4`](https://askubuntu.com/questions/849057/how-to-install-libsass-on-ubuntu-16-04)



### Other distributions:


#### Prerequisites

You need to have `python3-gobject` binding and those libraries/executables:
 - `glib-compile-schemas`
 - `gdk-pixbuf-pixdata`
 - `sassc>=3.4`
 - `gtk3>=3.18`
 - `bc`
 - `sed`
 - `rsvg-convert` from `librsvg`
 - `imagemagick`
 - `zip` - optional, for spotify theme
 - `optipng` - optional, for Materia theme
 - `parallel` - optional, for Materia theme
 - `inkscape` - optional, for Materia theme

For GTK2 you need murrine engine which can be not installed by default.

#### Installation

```sh
git clone https://github.com/actionless/oomox.git --recursive
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



#### Review articles

To learn more about using the application you can check these articles: 

  * https://delightlylinux.wordpress.com/2016/08/22/customize-theme-colors-with-oomox/
  * http://www.webupd8.org/2016/05/easily-create-your-own-numix-based-gtk.html
  * http://www.webupd8.org/2016/06/tool-to-customize-numix-theme-colors.html



#### Demo video

One of the users, Spatry, made this cool demo video:

https://www.youtube.com/watch?v=Dh5TuIYQ6jo
