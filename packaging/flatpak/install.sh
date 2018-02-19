#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
SCRIPT_DIR=$(readlink -e $(dirname "${0}"))

cd "${SCRIPT_DIR}"/../..

rm -r ./plugins/{oomoxify,theme_materia}
sed -i -e 's/\\/opt\\/oomox\\//\\/app\\/opt\\/oomox\\//g' ./packaging/bin/*
./packaging/install.sh ./ /app/
python3 -O -m compileall /app/opt/oomox/oomox_gui

cp -prf /app/usr/* /app/
rm -r /app/usr/
