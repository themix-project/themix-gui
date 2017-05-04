#!/usr/bin/env bash
set -ueo pipefail
root="$(readlink -f $(dirname "$0"))"


print_usage() {
	echo "
usage:
	$0 [-o OUTPUT_THEME_NAME] PRESET_NAME_OR_PATH

examples:
       $0 monovedek
       $0 -o my-theme-name ./colors/retro/twg"
	exit 1
}


darker_channel() {
	value=${1}
	light_delta=${2}
	result=$(echo "ibase=16; ${value} - ${light_delta}" | bc)
	if [[ ${result} -lt 0 ]] ; then
		result=0
	fi
	if [[ ${result} -gt 255 ]] ; then
		result=255
	fi
	echo "${result}"
}


darker() {
	hexinput=$(echo $1 | tr '[:lower:]' '[:upper:]')
	light_delta=${2-10}

    a=`echo $hexinput | cut -c-2`
    b=`echo $hexinput | cut -c3-4`
    c=`echo $hexinput | cut -c5-6`

	r=$(darker_channel ${a} ${light_delta})
	g=$(darker_channel ${b} ${light_delta})
	b=$(darker_channel ${c} ${light_delta})

	printf '%02x%02x%02x\n' ${r} ${g} ${b}
}


while [[ $# > 0 ]]
do
	case ${1} in
		-h|--help)
			print_usage
			exit 0
		;;
		-o|--output)
			OUTPUT_THEME_NAME="${2}"
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


light_folder_base_fallback="$(darker ${SEL_BG} -10)"
medium_base_fallback="$(darker ${SEL_BG} 37)"
dark_stroke_fallback="$(darker ${SEL_BG} 50)"

light_folder_base="${ICONS_LIGHT_FOLDER-$light_folder_base_fallback}"
light_base="${ICONS_LIGHT-$SEL_BG}"
medium_base="${ICONS_MEDIUM-$medium_base_fallback}"
dark_stroke="${ICONS_DARK-$dark_stroke_fallback}"


OUTPUT_THEME_NAME="${OUTPUT_THEME_NAME-oomox-$THEME}"
output_dir="${HOME}/.icons/${OUTPUT_THEME_NAME}"
mkdir -p "${output_dir}" || true

tmp_dir="$(mktemp -d)"
function post_clean_up {
	rm -r "${tmp_dir}" || true
}
trap post_clean_up EXIT SIGHUP SIGINT SIGTERM


cp -r "${root}/gnome-colors/"* "${tmp_dir}/"
cd "${tmp_dir}"

cat > ./themes/"${OUTPUT_THEME_NAME}" <<EOF
Name=${OUTPUT_THEME_NAME}
Distribution=gnome-colors
LightFolderBase=#${light_folder_base}
LightBase=#${light_base}
MediumBase=#${medium_base}
DarkStroke=#${dark_stroke}
EOF

make "${OUTPUT_THEME_NAME}"
cp -r ./"${OUTPUT_THEME_NAME}"/* "${output_dir}"/
