#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

release_msg="$1"

plugin_name=oomoxify
pkg_name=themix-export-spotify-git
plugin_subdir=/
pkgbuild_path=plugins/oomoxify/packaging/arch/PKGBUILD

SCRIPT_DIR="$(dirname "$0")"
"${SCRIPT_DIR}/release_plugin.sh" \
	"$plugin_name" \
	"$pkg_name" \
	"$plugin_subdir" \
	"$release_msg" \
	"$pkgbuild_path"
