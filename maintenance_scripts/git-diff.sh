#!/bin/sh
git -c 'color.status=always' status | grep -v -e colors/ -e dumpster/ -e git-diff -e '\[31mgtk-theme\[m' -e env35/
