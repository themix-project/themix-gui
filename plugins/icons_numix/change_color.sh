#!/usr/bin/env bash
set -ueo pipefail
root="$(readlink -f "$(dirname "$0")")"


print_usage() {
	echo "
usage:
	$0 [-o OUTPUT_THEME_NAME] [-c COLOR] PRESET_NAME_OR_PATH

examples:
	$0 -o droid_test_3 -c 5e468c
	$0 monovedek
	$0 -o my-theme-name ./colors/lcars"
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
	hexinput=$(echo "$1" | tr '[:lower:]' '[:upper:]')
	light_delta=${2-10}

	a=$(echo "$hexinput" | cut -c-2)
	b=$(echo "$hexinput" | cut -c3-4)
	c=$(echo "$hexinput" | cut -c5-6)

	r=$(darker_channel "${a}" "${light_delta}")
	g=$(darker_channel "${b}" "${light_delta}")
	b=$(darker_channel "${c}" "${light_delta}")

	printf '%02x%02x%02x\n' "${r}" "${g}" "${b}"
}


while [[ $# -gt 0 ]]
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
		-c|--color)
			ICONS_ARCHDROID="${2}"
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
	if [[ -z "${OUTPUT_THEME_NAME:-}" ]] && [[ -z "${ICONS_ARCHDROID:-}" ]]; then
		print_usage
	else
		THEME="${OUTPUT_THEME_NAME}"
	fi
else
	# shellcheck disable=SC1090
	if [[ ${THEME} == */* ]] || [[ ${THEME} == *.* ]] ; then
		source "$THEME"
		THEME=$(basename "${THEME}")
	else
		source "${root}/colors/$THEME"
	fi
fi


OUTPUT_THEME_NAME="${OUTPUT_THEME_NAME-oomox-$THEME-flat}"
output_dir="${HOME}/.icons/${OUTPUT_THEME_NAME}"

tmp_dir="$(mktemp -d)"
function post_clean_up {
	rm -r "${tmp_dir}" || true
}
trap post_clean_up EXIT SIGHUP SIGINT SIGTERM


light_folder_base_fallback="$(darker "${SEL_BG}" -10)"
medium_base_fallback="$(darker "${SEL_BG}" 37)"
dark_stroke_fallback="$(darker "${SEL_BG}" 50)"

NUMIX_COLOR1="${ICONS_LIGHT_FOLDER-$light_folder_base_fallback}"
#light_base="${ICONS_LIGHT-$SEL_BG}"
NUMIX_COLOR2="${ICONS_MEDIUM-$medium_base_fallback}"
NUMIX_COLOR3="${ICONS_DARK-$dark_stroke_fallback}"

NUMIX_STYLE="${ICONS_NUMIX_STYLE-0}"  # 0..5
NUMIX_SHAPE="${ICONS_NUMIX_SHAPE-normal}"  # normal | circle | square


echo ":: Copying theme template..."
#cp -r /usr/share/icons/Numix "${tmp_dir}"/
cp -r "${root}/numix-icon-theme/Numix" "${tmp_dir}"/
cp -r "${root}/numix-folders/styles/${NUMIX_STYLE}/"* "${tmp_dir}"/
echo "== Template was copied to ${tmp_dir}"


echo ":: Replacing colors..."
find "${tmp_dir}"/Numix/*/{actions,places}/*custom* \
	-exec sed -i --follow-symlinks "s/replacecolour1/#${NUMIX_COLOR1}/g" {} \; \
	-exec sed -i --follow-symlinks "s/replacecolour2/#${NUMIX_COLOR2}/g" {} \; \
	-exec sed -i --follow-symlinks "s/replacecolour3/#${NUMIX_COLOR3}/g" {} \;


echo ":: Creating symlinks..."
currentcolour=$(readlink "${tmp_dir}"/Numix/16/places/folder.svg | cut -d '-' -f 1)
links=$(find -L "${tmp_dir}"/Numix/*/{actions,places} -xtype l)
for link in $links; do
	if [[ $link == *folder_color* ]]; then
		continue
	fi
	newlink=$(readlink "${link}");
	if [[ $newlink == *"$currentcolour"* ]]; then
		newlink=${newlink/${currentcolour}/custom}
		ln -sf "${newlink}" "${link}"
	fi
done


echo ":: Applying style..."
if [[ ${NUMIX_SHAPE} = 'circle' ]] ; then
	cp -rH "${tmp_dir}/Numix-Circle/"* "${tmp_dir}"/Numix/
elif [[ ${NUMIX_SHAPE} = 'square' ]] ; then
	cp -rH "${tmp_dir}/Numix-Square/"* "${tmp_dir}"/Numix/
fi


echo ":: Exporting theme..."
sed -i \
	-e "s/Name=Numix/Name=${OUTPUT_THEME_NAME}/g" \
	"${tmp_dir}"/Numix/index.theme

if [[ -d "${output_dir}" ]] ; then
	rm -r "${output_dir}"
fi
mkdir -p "${output_dir}"
mv "${tmp_dir}"/Numix/* "${output_dir}/"

echo "== Theme was generated in ${output_dir}"
