#!/usr/bin/env bash
set -eu
cd $(readlink -e $(dirname "${0}"))
cp Recipe Dockerfile .dockerignore ../
cd ../
docker build ./ -t oomox-app-image
docker rm -v oomox-app-image-container || true
docker create --name oomox-app-image-container oomox-app-image
docker cp oomox-app-image-container:/src/out/Oomox-Theme-Designer-x86_64.AppImage ./
rm Recipe Dockerfile .dockerignore
