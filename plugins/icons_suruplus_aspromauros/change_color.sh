#!/usr/bin/env bash
set -ueo pipefail
root="$(readlink -f "$(dirname "$0")")"


print_usage() {
	local -i exit_code="$1"

	echo "
usage:
	$0 [-o OUTPUT_THEME_NAME] [-c COLOR] PRESET_NAME_OR_PATH

examples:
	$0 -o droid_test_3 -c 5e468c
	$0 monovedek
	$0 -o my-theme-name ./colors/lcars"

	exit "${exit_code:-1}"
}


darker_channel() {
	local value="0x$1"
	local light_delta="0x$2"
	local -i result

	result=$(( value - light_delta ))

	(( result < 0   )) && result=0
	(( result > 255 )) && result=255

	echo "$result"
}


darker() {
	local hexinput="$1"
	local light_delta=${2-10}

	r=$(darker_channel "${hexinput:0:2}" "$light_delta")
	g=$(darker_channel "${hexinput:2:2}" "$light_delta")
	b=$(darker_channel "${hexinput:4:2}" "$light_delta")

	printf '%02x%02x%02x\n' "$r" "$g" "$b"
}


while [[ $# -gt 0 ]]
do
	case "$1" in
		-h|--help)
			print_usage 0
			;;
		-o|--output)
			OUTPUT_THEME_NAME="$2"
			shift
			;;
		-d|--destdir)
			output_dir="$2"
			shift
			;;
		-c|--color)
			ICONS_COLOR="${2#\#}"  # remove leading hash symbol
			shift
			;;
		-*)
			echo "unknown option $1"
			print_usage 2
			;;
		*)
			THEME="$1"
			;;
	esac
	shift
done

if [ -z "${THEME:-}" ]; then
	[ -n "${OUTPUT_THEME_NAME:-}" ] || print_usage 1
	[ -n "${ICONS_COLOR:-}" ] || print_usage 1

	THEME="$OUTPUT_THEME_NAME"
else
	# shellcheck disable=SC1090
	if [ -f "$THEME" ]; then
		source "$THEME"
		THEME=$(basename "$THEME")
	elif [ -f "$root/colors/$THEME" ]; then
		source "$root/colors/$THEME"
	else
		echo "'$THEME' preset not found."
		exit 1
	fi
fi


tmp_dir="$(mktemp -d)"
function post_clean_up {
	rm -r "$tmp_dir" || true
}
trap post_clean_up EXIT SIGHUP SIGINT SIGTERM


: "${ICONS_COLOR:=$SEL_BG}"
: "${OUTPUT_THEME_NAME:=oomox-$THEME}"

output_dir="${output_dir:-$HOME/.icons/$OUTPUT_THEME_NAME}"

light_folder_fallback="$ICONS_COLOR"
medium_base_fallback="$(darker "$ICONS_COLOR" 20)"
dark_stroke_fallback="$(darker "$ICONS_COLOR" 56)"

SURUPLUS_GRADIENT_ENABLED=$(echo "${SURUPLUS_GRADIENT_ENABLED-False}" | tr '[:upper:]' '[:lower:]')

: "${ICONS_LIGHT_FOLDER:=$light_folder_fallback}"
: "${ICONS_MEDIUM:=$medium_base_fallback}"
: "${ICONS_DARK:=$dark_stroke_fallback}"
: "${ICONS_SYMBOLIC_ACTION:=${MENU_FG:-}}"
: "${ICONS_SYMBOLIC_PANEL:=${HDR_FG:-}}"


echo ":: Copying theme template..."
cp -R "$root/suru-plus-aspromauros/Suru++-Asprómauros" "$tmp_dir/"
echo "== Template was copied to $tmp_dir"

if [ -n "${ICONS_SYMBOLIC_ACTION:-}" ]; then
	echo ":: Replacing symbolic actions colors..."
	find "$tmp_dir"/Suru++-Asprómauros/actions/{16,22,24,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/apps/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/devices/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/emblems/symbolic \
		"$tmp_dir"/Suru++-Asprómauros/emotes/symbolic \
		"$tmp_dir"/Suru++-Asprómauros/mimetypes/16 \
		"$tmp_dir"/Suru++-Asprómauros/panel/{16,22,24} \
		"$tmp_dir"/Suru++-Asprómauros/places/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/status/symbolic \
		-type f -name '*.svg' \
		-exec sed -i'' -e "s/ececec/$ICONS_SYMBOLIC_ACTION/g" '{}' \;
fi

if [ -n "${ICONS_SYMBOLIC_PANEL:-}" ]; then
	echo ":: Replacing symbolic panel colors..."
	find "$tmp_dir"/Suru++-Asprómauros/animations/{22,24} \
		-type f -name '*.svg' \
		-exec sed -i'' -e "s/d3dae3/$ICONS_SYMBOLIC_PANEL/g" '{}' \;
fi

if [ "$SURUPLUS_GRADIENT_ENABLED" = "true" ] && [ -n "${SURUPLUS_GRADIENT1:-}" ] && [ -n "${SURUPLUS_GRADIENT2:-}" ]; then
	echo ":: Replacing gradient colors..."
	find "$tmp_dir"/Suru++-Asprómauros/actions/{16,22,24,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/apps/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/devices/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/emblems/symbolic \
		"$tmp_dir"/Suru++-Asprómauros/emotes/symbolic \
		"$tmp_dir"/Suru++-Asprómauros/mimetypes/16 \
		"$tmp_dir"/Suru++-Asprómauros/panel/{16,22,24} \
		"$tmp_dir"/Suru++-Asprómauros/places/{16,symbolic} \
		"$tmp_dir"/Suru++-Asprómauros/status/symbolic \
		-type f -name '*.svg' \
		-exec sed -i'' \
			-e 's/fill="currentColor" class="ColorScheme-Text"/fill="url(#oomox)" class="ColorScheme-Text"/g' \
			-e 's/stroke="currentColor" class="ColorScheme-Text"/stroke="url(#oomox)" class="ColorScheme-Text"/g' \
			-e "s/efefe7/$SURUPLUS_GRADIENT1/g" \
			-e "s/8f8f8b/$SURUPLUS_GRADIENT2/g" '{}' \;
fi

echo ":: Exporting theme..."
sed -i \
	-e "s/^Name=.*/Name=$OUTPUT_THEME_NAME/g" \
	-e '/^Name\[.*$/d' \
	"$tmp_dir/Suru++-Asprómauros/index.theme"

if [ -d "$output_dir" ] ; then
	rm -r "$output_dir"
fi

mkdir -p "$output_dir"
mv "$tmp_dir"/Suru++-Asprómauros/* "$output_dir/"

echo "== Theme was generated in $output_dir"
