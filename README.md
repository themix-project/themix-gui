oomox
=====

## numix fork with color changing script

### prerequisites:
You need to have `python3-gobject` binding and those executables:
```
glib-compile-schemas
gdk-pixbuf-pixdata
sass
```

#### Arch Linux:
```
yaourt -S glib2 gdk-pixbuf2 ruby-sass python-gobject
```
@TODO: create PKGBUILD


### usage:

#### GUI:
```
git clone https://github.com/actionless/oomox.git
./gui.sh
```
![Screenshot GUI 1](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui.png "Screenshot GUI 1")

![Screenshot GUI 2](https://raw.githubusercontent.com/actionless/oomox/master/screenshot_gui_retro.png "Screenshot GUI 2")

#### CLI:
```sh
git clone https://github.com/actionless/oomox.git
cd oomox
ls colors
./change_color.sh gnome_noble  # or other theme from above
```


next select oomox_current in your appearance config tool (for example, _lxappearance_)

