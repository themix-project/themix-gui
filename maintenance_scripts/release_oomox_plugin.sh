#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

release_msg="$1"

plugin_name=theme_oomox
pkg_name=themix-theme-oomox-git
plugin_subdir=/
pkgbuild_path="plugins/${plugin_name}/packaging/arch/PKGBUILD"

SCRIPT_DIR="$(dirname "$0")"
"${SCRIPT_DIR}/release_plugin.sh" \
	"$plugin_name" \
	"$pkg_name" \
	"$plugin_subdir" \
	"$release_msg" \
	"$pkgbuild_path"
