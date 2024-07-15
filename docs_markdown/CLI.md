### CLI


#### Multi-Export CLI


```sh
themix-multi-export --help
```

or

```sh
./multi_export_cli.sh --help
```

Example multi-export config file could be found in `./export_config_examples` directory of this git repository.

When using Multi-Export from GUI your multi-export layout would be automatically saved to `~/.config/oomox/export_config/multi_export_*.json` files.


#### Theme/Icon Plugins CLI

If your prefer CLI interface, refer to `change_color.sh` scripts inside `./plugins/`. For `xresources` and `random` themes in CLI use palettes from `/opt/oomox/scripted_colors/` directory. Using scripted palettes enables you to use bash to write simple generators for dynamic themes (as alternative to plugins in oomox-gui). GUI is not attempting to execute any scripted palettes with bash because downloading such scripted themes from random places could lead to unexpected result so you can use them only with CLI, when you really know what you're doing.


#### Base16 export CLI

In the directory with Base16 plugin you could run the CLI as well:
```
python cli.py --help
```


#### Spotify:

Spotify theme can be also exported from GUI, but if you prefer commandline interface:

```sh
./plugins/oomoxify/oomoxify.sh ./colors/gnome-colors/shiki-noble
```

Also you can normalize font weight with `-w` argument, see `-h` for usage.

Spotify theme settings are backed up to `~/.config/oomox/spotify_backup`. To undo the changes made by oomoxify, these files can be copied back to their original location `/usr/share/spotify/Apps`. Spotify can also be reinstalled, which will reset these files as well.

Users running Spotify under Flatpak should set their "Spotify path" in oomox to `/var/lib/flatpak/app/com.spotify.Client/current/active/files/extra/share/spotify/Apps` in order to apply the theme.
