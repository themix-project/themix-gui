#!/usr/bin/fish
for f in *.svg; rsvg-convert -d 300 -p 300 -f svg $f -o $f.bak ; mv $f.bak $f ; end
