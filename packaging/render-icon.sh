#!/bin/bash
set -ueo pipefail

sizes=('16' '24' '32' '48' '512')

for size in "${sizes[@]}"; do
  inkscape -i "$size" -e "com.github.themix-project.oomox-$size.png" "com.github.themix-project.oomox.svg"
done
