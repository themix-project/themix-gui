#!/bin/bash
set -ueo pipefail
root="$(readlink -e $(dirname "$0"))"


spotify_apps_path="/usr/share/spotify/Apps"
backup_dir="${HOME}/.config/oomox/spotify_backup"


print_usage() {
	echo "
usage:
$0 [-s /path/to/spotify/Apps] [-f] PRESET_NAME_OR_PATH

options:
	-s, --spotify-apps-path		path to spotify/Apps
	-f, --system-font		use system font

examples:
	$0 monovedek
	$0 -f ./colors/gnome-colors/shiki-noble
	$0 -o /opt/spotify/Apps ./colors/retro/twg"
	exit 1
}


darker() {
	hexinput=$(echo $1 | tr '[:lower:]' '[:upper:]')
	light_delta=${2-10}

    a=`echo $hexinput | cut -c-2`
    b=`echo $hexinput | cut -c3-4`
    c=`echo $hexinput | cut -c5-6`

    r=`echo "ibase=16; $a - $light_delta" | bc`
    g=`echo "ibase=16; $b - $light_delta" | bc`
    b=`echo "ibase=16; $c - $light_delta" | bc`

	echo $(echo "obase=16; $r" | bc ; echo "obase=16; $g" | bc ;echo "obase=16; $b" | bc) | tr -d ' '
}


while [[ $# > 0 ]]
do
	case ${1} in
		-h|--help)
			print_usage
			exit 0
		;;
		-f|--system-font)
			use_system_font="True"
		;;
		-s|--spotify-apps-path)
			spotify_apps_path="${2}"
			shift
		;;
		*)
			if [[ "${1}" == -* ]] || [[ ${THEME-} ]]; then
				echo "unknown option ${1}"
				print_usage
				exit 2
			fi
			THEME="${1}"
		;;
	esac
	shift
done

if [[ -z "${THEME:-}" ]] ; then
	print_usage
fi

if [[ ${THEME} == */* ]] || [[ ${THEME} == *.* ]] ; then
	source "$THEME"
	THEME=$(basename ${THEME})
else
	source "${root}/colors/$THEME"
fi


main_bg="${BG}"
area_bg="${TXT_BG}"
selected_row_bg="$(darker ${BG})"
selected_area_bg="$(darker ${TXT_BG} 20)"

sidebar_fg="${FG}"
main_fg="${FG}"
accent_fg="$(darker ${BTN_BG} 30)"

hover_text="${SEL_BG}"
active_selection_color="${SEL_BG}"
inactive_selection_color="$(darker ${SEL_BG})"


tmp_dir="$(mktemp -d)"
output_dir="$(mktemp -d)"
function post_clean_up {
	rm -r "${tmp_dir}" || true
	rm -r "${output_dir}" || true
}
trap post_clean_up EXIT SIGHUP SIGINT SIGTERM

if [[ ! -d "${backup_dir}" ]] ; then
	mkdir "${backup_dir}"
	cp -prf "${spotify_apps_path}"/*.spa "${backup_dir}/"
fi


cd "${root}"
for file in $(ls "${backup_dir}"/*.spa | grep -v messages) ; do
	filename="$(basename "${file}")"
	echo "${filename}"
	cp "${file}" "${tmp_dir}/"
	cd "${tmp_dir}"
	unzip "./${filename}" > /dev/null
	if [[ -d ./css/ ]] && [[ -f ./css/style.css ]] ; then
		for css in $(ls ./css/*.css); do
			if [ ! -z "${use_system_font:-}" ] ; then
				replace_font=sans-serif
				sed -i \
					-e "s/'spotify-circular'/${replace_font}/g" \
					-e "s/'circular_sp_.*'/${replace_font}/g" \
					-e "s/font-family: circular_.*/font-fmaily: ${replace_font}/g" \
					-e "s/Monaco/monospace/g" \
					-e "s/font-weight: 200/font-weight: 400/g" \
					-e "s/font-weight: 100/font-weight: 400/g" \
					"${css}" || true
			fi
			sed -i \
				-e "s/282828/oomox_main_bg/g" \
				-e "s/181818/oomox_area_bg/g" \
				-e "s/333333/oomox_selected_row_bg/g" \
				-e "s/404040/oomox_selected_area_bg/g" \
				-e "s/ffffff/oomox_accent_fg/gI" \
				-e "s/fcfcfc/oomox_hover_text/gI" \
				-e "s/1ed760/oomox_active_selection_color/gI" \
				-e "s/1ed660/oomox_active_selection_color/gI" \
				-e "s/1db954/oomox_inactive_selection_color/gI" \
				-e "s/a0a0a0/oomox_main_fg/gI" \
				-e "s/adafb2/oomox_sidebar_fg/gI" \
				"${css}"
			sed -i \
				-e "s/oomox_main_bg/${main_bg}/g" \
				-e "s/oomox_area_bg/${area_bg}/g" \
				-e "s/oomox_selected_row_bg/${selected_row_bg}/g" \
				-e "s/oomox_selected_area_bg/${selected_area_bg}/g" \
				-e "s/oomox_accent_fg/${accent_fg}/gI" \
				-e "s/oomox_hover_text/${hover_text}/gI" \
				-e "s/oomox_active_selection_color/${active_selection_color}/gI" \
				-e "s/oomox_inactive_selection_color/${inactive_selection_color}/gI" \
				-e "s/oomox_main_fg/${main_fg}/gI" \
				-e "s/oomox_sidebar_fg/${sidebar_fg}/gI" \
				"${css}"
			zip "./${filename}" "${css}" > /dev/null
		done
		cd "${tmp_dir}"
		mv "./${filename}" "${output_dir}/"
	fi
	rm "${tmp_dir}/"* -r
done

sudo cp "${output_dir}/"* "${spotify_apps_path}"/
