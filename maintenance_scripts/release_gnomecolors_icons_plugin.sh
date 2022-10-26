#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

release_msg="$1"

plugin_name=icons_gnomecolors
pkg_name=themix-icons-gnome-colors-git
plugin_subdir=/gnome-colors-icon-theme

SCRIPT_DIR="$(dirname "$0")"
"${SCRIPT_DIR}/release_plugin.sh" \
	"$plugin_name" \
	"$pkg_name" \
	"$plugin_subdir" \
	"$release_msg"
