oomox
=====

Graphical application for generating different color variations of Numix theme (GTK2, GTK3)

  * [Arch Linux](#arch-linux "")
  * [Ubuntu](#ubuntu "")
  * [Other distributions](#other-distributions "")
  * [Using with tiling WMs](#using-with-tiling-wms "")
  * [Spotify](#spotify "")
  * [Review article](#review-article "")
  * [Demo video](#demo-video "")


![Screenshot GUI 1](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui.png "Screenshot GUI 1")

![Screenshot GUI 2](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui_retro.png "Screenshot GUI 2")

### Arch Linux:

#### Install

```
yaourt -S oomox-git
```

#### GUI

```
oomox-gui
```


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
}
```


### Other distributions:

#### Prerequisites

You need to have `python3-gobject` binding and those executables:
 - `glib-compile-schemas`
 - `gdk-pixbuf-pixdata`
 - `sass`
For GTK2 you need murrine engine which can be not installed by default.

##### Ubuntu

```
sudo apt install ruby libgdk-pixbuf2.0-dev libxml2-utils python3-gi gtk2-engines-murrine
sudo gem install sass
```

#### GUI

```sh
git clone https://github.com/actionless/oomox.git
cd oomox
./gui.sh
```

#### CLI:
```sh
git clone https://github.com/actionless/oomox.git
cd oomox
ls colors
./change_color.sh gnome_noble  # or other theme from above
```


next select oomox_current in your appearance config tool (for example, _lxappearance_)


#### Spotify:
```sh
git clone https://github.com/actionless/oomox.git
cd oomox
ls colors
./oomoxify.sh gnome_noble  # or other theme from above
```
Make sure to remove `~/.config/oomox/spotify_backup` when upgrading Spotify to the new version.

Also you can replace font with `-f` argument, see `-h` for usage.


#### Review article

To learn more about it you can check this article: http://www.webupd8.org/2016/05/easily-create-your-own-numix-based-gtk.html

#### Demo video

One of the users, Spatry, made this cool demo video:

[![video](https://img.youtube.com/vi/Dh5TuIYQ6jo/0.jpg)](https://www.youtube.com/watch?v=Dh5TuIYQ6jo)
