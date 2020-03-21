#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

TEST_DIR=$(readlink -e "$(dirname "${0}")")
SCRIPT_DIR="$(readlink -e "${TEST_DIR}"/..)"

(
	cd "${SCRIPT_DIR}"
	# shellcheck disable=SC2046
	shellcheck $(find . \
		-name '*.sh' \
		-not -path './plugins/icons_archdroid/archdroid-icon-theme/*' \
		-not -path './plugins/icons_gnomecolors/gnome-colors-icon-theme/*' \
		-not -path './plugins/icons_papirus/papirus-icon-theme/*' \
		-not -path './plugins/icons_suruplus/suru-plus/*' \
		-not -path './plugins/icons_suruplus_aspromauros/suru-plus-aspromauros/*' \
		-not -path './plugins/base16/*.tmp/*' \
		-not -path './plugins/oomoxify/*' \
		-not -path './plugins/theme_arc/arc-theme/*' \
		-not -path './plugins/theme_materia/materia-theme/*' \
		-not -path './plugins/theme_oomox/gtk-theme/*' \
		-or -path './packaging/bin/*' \
	)
)

echo ':: shellcheck passed ::'
exit 0
