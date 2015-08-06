Numix is a modern flat theme with a combination of light and dark elements. It supports Gnome, Unity, XFCE and Openbox.

Numix is a part of the [Numix Project](http://numixproject.org).

### Manual installation

First, you need to compile the theme using the [Sass](http://sass-lang.com/) compiler.

To install Sass, install ruby and the gem command using your distro's package manager. Then install `sass` with the `gem` command,

`gem install sass`

You'll also need the following commands in your path to generate the gresource binary. Install them using your distro's package manager.

* `glib-compile-schemas`
* `gdk-pixbuf-pixdata`

After installing all the dependencies, switch to the cloned directory and, run the following in Terminal,

```
make
sudo make install
```

To set the theme in Gnome, run the following commands in Terminal,

```
gsettings set org.gnome.desktop.interface gtk-theme "Numix"
gsettings set org.gnome.desktop.wm.preferences theme "Numix"
```

To set the theme in Xfce, run the following commands in Terminal,

```
xfconf-query -c xsettings -p /Net/ThemeName -s "Numix"
xfconf-query -c xfwm4 -p /general/theme -s "Numix"
```

### Requirements

GTK+ 3.16 or above

Murrine theme engine

### Code and license

Report bugs or contribute at [GitHub](https://github.com/shimmerproject/Numix)

License: GPL-3.0+
