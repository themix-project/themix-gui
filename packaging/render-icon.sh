#!/bin/bash
set -ueo pipefail

sizes=('16' '24' '32' '48' '512')

for size in "${sizes[@]}"; do
  inkscape -i "$size" -e "com.github.themix_project.Oomox-$size.png" "com.github.themix_project.Oomox.svg"
done
