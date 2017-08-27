oomox
=====

Graphical application for generating different color variations of a Numix-based and Flat-Plat themes (GTK2, GTK3), Gnome-Colors and Archdroid icon themes.

  * [Arch Linux](#arch-linux "")
  * [Ubuntu](#ubuntu "")
  * [Fedora](#fedora "")
  * [Other distributions](#other-distributions "")
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Spotify](#spotify "")
  * [Review articles/Usage instructions](#review-articles "")
  * [Demo video](#demo-video "")


![Screenshot GUI](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui.png "Screenshot GUI")
[Big screenshot with number of examples](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)
![Screenshot Themes](https://raw.githubusercontent.com/actionless/oomox/master/screenshot.png "Screenshot Themes")


### Arch Linux:

#### Install

```
pacaur -S oomox-git
```

#### GUI

```
oomox-gui
```



### Ubuntu

Ubuntu 16.10, 16.04 and 15.10 (and other ubuntu-based like Linux Mint 18 and newer) users can install Oomox by using the main WebUpd8 PPA:

```bash
sudo add-apt-repository ppa:nilarimogard/webupd8
sudo apt update
sudo apt install oomox
```

If you don't want to add the PPA, you can download the deb from [here](http://ppa.launchpad.net/nilarimogard/webupd8/ubuntu/pool/main/o/oomox/ "").

For older Ubuntu releases install the dependencies manually and next follow general installation instructions [below](#installation "").

```
sudo apt install libgdk-pixbuf2.0-dev libxml2-utils python3-gi gtk2-engines-murrine bc sed zip inkscape imagemagick optipng parallel
```

And install `sassc>=3.4`: https://askubuntu.com/questions/849057/how-to-install-libsass-on-ubuntu-16-04



### Fedora

Fedora 24 and 25 users users can install Oomox by using a third party copr repository:
```bash
sudo dnf copr enable tcg/themes
sudo dnf install oomox
```



### Other distributions:


#### Prerequisites

You need to have `python3-gobject` binding and those executables:
 - `glib-compile-schemas`
 - `gdk-pixbuf-pixdata`
 - `sassc>=3.4`
 - `gtk3>=3.18`
 - `bc`
 - `sed`
 - `zip` - optional, for spotify theme
 - `inkscape` - optional, for gnome-colors icons and Flat-Plat theme
 - `imagemagick` - optional, for gnome-colors icons
 - `optipng` - optional, for Flat-Plat theme
 - `parallel` - optional, for Flat-Plat theme

For GTK2 you need murrine engine which can be not installed by default.

#### Installation

```sh
git clone https://github.com/actionless/oomox.git --recursive
cd oomox
# if you need to generate French locale:
make -f po.mk install
```

#### GUI

```sh
./gui.sh
```


#### CLI:
```sh
./gtk-theme/change_color.sh ./colors/gnome-colors/shiki-noble
```

next select oomox-current in your appearance config tool (for example, _lxappearance_)


#### Icons:

For icons you need to have `inkscape` and `imagemagick` installed.

To generate `gnome-colors` iconset with the selected colorscheme:

```sh
./gnome_colors.sh ./colors/gnome-colors/shiki-noble
```

next select oomox-current in your appearance config tool (for example, _lxappearance_)


#### Spotify:
```sh
./oomoxify.sh ./colors/gnome-colors/shiki-noble
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
