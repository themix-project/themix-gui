#!/bin/sh
git -c 'color.status=always' status \
    | grep -v \
        -e colors/ \
        -e dumpster/ \
        -e '\[31mgtk-theme\[m' \
        -e 'env.*/' \
        -e '[^/]*png' \
        -e '[^/]git-status' \
        -e 'misc' \
        -e 'modified:   plugins/.* (untracked content)' \
        -e 'plugins/theme_arc/arc-theme' \
        -e 'plugins/theme_materia/materia-theme'
