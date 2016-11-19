## Numix
##### A modern flat theme with a combination of light and dark elements. It supports GNOME, Unity, Xfce and Openbox.
[![By The Numix Project](https://img.shields.io/badge/By-The%20Numix%20Project-f0544c.svg?style=flat-square)](https://numixproject.org/) &nbsp;[![Circle CI](https://img.shields.io/circleci/project/numixproject/numix-gtk-theme/master.svg?circle-token=b14acf911433d315298235b0c2fbf7b2670a92a8&maxAge=2592000&style=flat-square)](https://circleci.com/gh/numixproject/numix-gtk-theme/tree/master) &nbsp;[![GitHub release](https://img.shields.io/github/release/numixproject/numix-gtk-theme.svg?maxAge=3600&style=flat-square)](https://github.com/numixproject/numix-gtk-theme/releases/latest) &nbsp;![Supports GTK+ 3.18](https://img.shields.io/badge/GTK%2B-3.18-4a90d9.svg?style=flat-square) &nbsp;![Supports GTK+ 3.20](https://img.shields.io/badge/GTK%2B-3.22-4a90d9.svg?style=flat-square)

## Install It

### Official Distro Packages
|Distro|Install Command/Links|
|:----:|:----:|
|![arch](https://dl.dropboxusercontent.com/u/60521097/archlogo26x26.png)&nbsp;![antergos](https://dl.dropboxusercontent.com/u/60521097/logo-square26x26.png)|`sudo pacman -S numix-themes`|
|![openSUSE](https://dl.dropboxusercontent.com/u/60521097/Geeko-button-bling7.png)|[1 Click Install](http://software.opensuse.org/ymp/openSUSE:Factory/standard/numix-gtk-theme.ymp) &nbsp;\|&nbsp; [OBS Repo](http://software.opensuse.org/download.html?project=openSUSE%3AFactory&package=numix-gtk-theme)|
|![fedora](https://dl.dropboxusercontent.com/u/60521097/fedora-logo.png)|`sudo dnf install numix-gtk-theme`|
|[![debian](https://www.debian.org/logos/openlogo-nd-25.jpg)](https://www.debian.org/)&nbsp;![ubuntu](https://dl.dropboxusercontent.com/u/60521097/ubuntu_orange_hex.png)|`apt install numix-gtk-theme`|

## Build It

First, you need to compile the theme using the [Sass](http://sass-lang.com/) compiler.

To install Sass, install Ruby and the gem command using your distribution's package manager. Then install `sass` with the `gem` command,

`gem install sass`

You'll also need the ```glib-compile-schemas``` and  ```gdk-pixbuf-pixdata``` commands in your path to generate the gresource binary. Install them using your distribution's package manager.

#### Debian, Ubuntu

 ```sh
sudo apt-get install libglib2.0-dev libgdk-pixbuf2.0-dev libxml2-utils
```

#### Fedora

```sh
sudo dnf install glib2-devel gdk-pixbuf2-devel
```

#### Arch Linux

```sh
sudo pacman -S glib2 gdk-pixbuf2
```

After installing all the dependencies, switch to the cloned directory and, run the following in Terminal,

```sh
make
sudo make install
```

To set the theme in GNOME, run the following commands in Terminal,

```sh
gsettings set org.gnome.desktop.interface gtk-theme "Numix"
gsettings set org.gnome.desktop.wm.preferences theme "Numix"
```

To set the theme in Xfce, run the following commands in Terminal,

```sh
xfconf-query -c xsettings -p /Net/ThemeName -s "Numix"
xfconf-query -c xfwm4 -p /general/theme -s "Numix"
```

### For contributors
Start by reviewing the [guidelines for contributing](https://github.com/numixproject/numix-gtk-theme/blob/master/.github/CONTRIBUTING.md).

#### For developers
If you want to hack on the theme, make sure you have the `inotifywait` command available, which is used for watching and automatically building the files.

To start watching for changes, run the following,

```sh
make watch
```

If you change any assets, you'll need to regenerate the `gtk.gresource.xml` and `gtk.gresource` files. You can use [grrr](https://github.com/satya164/grrr) to do it easily.

### Requirements

GTK+ 3.18 or above

Murrine theme engine

### Code and license

Report bugs or contribute at [GitHub](https://github.com/numixproject/numix-gtk-theme)

License: GPL-3.0+
