Themix GUI designer
=====

[![Code Style](https://github.com/themix-project/oomox/actions/workflows/ci.yml/badge.svg)](https://github.com/themix-project/oomox/actions/workflows/ci.yml) [![Commit Activity](https://img.shields.io/github/commit-activity/y/themix-project/themix-gui?color=pink&logo=amp&logoColor=pink)](https://github.com/themix-project/themix-gui/graphs/commit-activity)

Graphical application for designing themes and exporting them using plugins, for example:
  * [Oomox](https://github.com/themix-project/oomox-gtk-theme/) and [Materia](https://github.com/nana-4/materia-theme/) themes (GTK2, GTK3, Cinnamon, GNOME, Openbox, Xfwm). Have a hack for HiDPI in gtk2.
  * Icons ([Archdroid](https://github.com/GreenRaccoon23/archdroid-icon-theme), [Gnome-Colors](https://www.gnome-look.org/p/1012497), [Numix](https://github.com/numixproject/numix-folders), [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), [Suru++](https://github.com/gusbemacbe/suru-plus) and [Suru++ Asprómauros](https://github.com/gusbemacbe/suru-plus-aspromauros)).
  * Base16 plugin, which  also allows a lot of app themes support like Alacritty, Emacs, GTK4, KDE, Qt5ct, Qt6ct, VIM and [many](https://github.com/chriskempson/base16-templates-source) more.

Import plugins also available, such as:
  * generating color palettes from image;
  * importing it from Xresources;
  * or [huge](https://github.com/chriskempson/base16-schemes-source/) collection of Base16 themes.

<a href="https://aur.archlinux.org/packages/themix-full-git"><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_aur.png" height="54"></a>
<a href="https://slackbuilds.org/result/?search=oomox&sv="><img src="https://raw.githubusercontent.com/themix-project/oomox/master/packaging/download_slackware.png" height="54"></a>
<a href="https://flathub.org/apps/details/com.github.themix_project.Oomox"><img src="https://flathub.org/assets/badges/flathub-badge-en.png" height="54"></a>
<a href="https://github.com/Botspot/pi-apps"><img src="https://github.com/Botspot/pi-apps/blob/master/icons/badge.png?raw=true" height="53" style="border-radius: 9px; border: 1px #bbb solid;"></a>


Table of contents:
  * [Installing with package manager](#installation "")
  * [Installing manually](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/Manual_Installation.md)
  * [CLI](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/CLI.md)
  * [Using with tiling WMs and other GTK3 CSS hacks](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/CSS_Hacks.md)
  * [Wiki](#wiki "")
  * [Review videos/Usage instructions](#review-articles-and-videos "")

<img src="https://raw.githubusercontent.com/themix-project/oomox/master/screenshots/pokedex_dawn.png" alt="Screenshot image import" style="max-width: 886px;">

<img src="https://raw.githubusercontent.com/themix-project/oomox/master/screenshots/screenshot_gui.png" alt="Screenshot GUI" style="max-width: 843px;">

[Big screenshot with number of generated themes 🔗](http://orig15.deviantart.net/e1ee/f/2016/320/1/9/oomox_1_0_rc1_by_actionless-daomhmd.jpg)

[Latest Oomox GTK theme screenshots 🔗](https://github.com/themix-project/oomox-gtk-theme/tree/master/screenshots)



## Installation


### Arch Linux

#### Install

```
pikaur -S themix-full-git
```

AUR helpers are [not officially supported by Arch Linux](https://wiki.archlinux.org/index.php/AUR_helpers), so you can also [install it manually](https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_packages) from [rolling-release PKGBUILD](https://aur.archlinux.org/packages/themix-full-git/).

#### Open the GUI

```
themix-gui
```


### Debian, Ubuntu, Linux Mint

##### deb-based releases are currently abandoned, this way works for installing older versions of Themix
see also: https://github.com/themix-project/oomox/issues/144

[Old instructions for Deb-like distros](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/Ubuntu_Old.md)


### Other distributions

[Install it manually or use that information for creating a package for your distro](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/Manual_Installation.md)






## Other Help Resources

[Using with tiling WMs and other GTK3 CSS hacks](https://github.com/themix-project/themix-gui/blob/master/docs_markdown/CSS_Hacks.md)


### Wiki

[https://github.com/themix-project/themix-gui/wiki](https://github.com/themix-project/themix-gui/wiki)

Direct file editing:

```
git clone git@github.com:themix-project/themix-gui.wiki.git
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
