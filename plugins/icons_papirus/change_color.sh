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

output_dir="$HOME/.icons/$OUTPUT_THEME_NAME"

light_folder_fallback="$ICONS_COLOR"
medium_base_fallback="$(darker "$ICONS_COLOR" 20)"
dark_stroke_fallback="$(darker "$ICONS_COLOR" 56)"

: "${ICONS_LIGHT_FOLDER:=$light_folder_fallback}"
: "${ICONS_MEDIUM:=$medium_base_fallback}"
: "${ICONS_DARK:=$dark_stroke_fallback}"
: "${ICONS_SYMBOLIC_ACTION:=${MENU_FG:-}}"
: "${ICONS_SYMBOLIC_PANEL:=${HDR_FG:-}}"


echo ":: Copying theme template..."
cp -R "$root/papirus-icon-theme/Papirus" "$tmp_dir/"
echo "== Template was copied to $tmp_dir"


echo ":: Replacing accent colors..."
for size in 22x22 24x24 32x32 48x48 64x64; do
	for icon_path in \
		"$tmp_dir/Papirus/$size/places/folder-custom"{-*,}.svg \
		"$tmp_dir/Papirus/$size/places/user-custom"{-*,}.svg
	do
		[ -f "$icon_path" ] || continue  # it's a file
		[ -L "$icon_path" ] && continue  # it's not a symlink

		new_icon_path="${icon_path/-custom/-oomox}"
		icon_name="${new_icon_path##*/}"
		symlink_path="${new_icon_path/-oomox/}"  # remove color suffix

		sed -e "s/value_light/$ICONS_LIGHT_FOLDER/g" \
			-e "s/value_dark/$ICONS_MEDIUM/g" \
			-e "s/323232/$ICONS_DARK/g" "$icon_path" > "$new_icon_path"

		ln -sf "$icon_name" "$symlink_path"
	done
done

if [ -n "${ICONS_SYMBOLIC_ACTION:-}" ]; then
	echo ":: Replacing symbolic actions colors..."
	find "$tmp_dir"/Papirus/{16x16,22x22,24x24}/actions \
		"$tmp_dir"/Papirus/16x16/{devices,places} \
		"$tmp_dir"/Papirus/symbolic \
		-type f -name '*.svg' \
		-exec sed -i'' -e "s/444444/$ICONS_SYMBOLIC_ACTION/g" '{}' \;
fi

if [ -n "${ICONS_SYMBOLIC_PANEL:-}" ]; then
	echo ":: Replacing symbolic panel colors..."
	find "$tmp_dir"/Papirus/{16x16,22x22,24x24}/panel \
		"$tmp_dir"/Papirus/{22x22,24x24}/animations \
		-type f -name '*.svg' \
		-exec sed -i'' -e "s/dfdfdf/$ICONS_SYMBOLIC_PANEL/g" '{}' \;
fi


echo ":: Exporting theme..."
sed -i \
	-e "s/Name=Papirus/Name=$OUTPUT_THEME_NAME/g" \
	"$tmp_dir/Papirus/index.theme"

if [ -d "$output_dir" ] ; then
	rm -r "$output_dir"
fi

mkdir -p "$output_dir"
mv "$tmp_dir"/Papirus/* "$output_dir/"

echo "== Theme was generated in $output_dir"
