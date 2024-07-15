### Using with tiling WMs

Create/append to `~/.config/gtk-3.0/gtk.css`:

```css
/* remove window title from Client-Side Decorations */
.solid-csd headerbar .title {
    font-size: 0;
}

/* hide extra window decorations/double border */
window decoration {
    margin: 0;
    border: none;
    padding: 0;
}
```


### Extra GTK3 CSS hacks

Create/append to `~/.config/gtk-3.0/gtk.css`:

```css
* {
  text-shadow: none;
}
```
