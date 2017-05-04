#!/usr/bin/env bash
set -ueo pipefail
root="$(readlink -f $(dirname "$0"))"


print_usage() {
	echo "
usage:
	$0 [-o OUTPUT_THEME_NAME] PRESET_NAME_OR_PATH

examples:
       $0 monovedek
       $0 -o my-theme-name ./colors/lcars"
	exit 1
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


lime="CDDC39"
icons_color="${ICONS_ARCHDROID-$SEL_BG}"


OUTPUT_THEME_NAME="${OUTPUT_THEME_NAME-oomox-$THEME-flat}"
output_dir="${HOME}/.icons/${OUTPUT_THEME_NAME}"
mkdir -p "${output_dir}" || true

cp -r "${root}/archdroid-icon-theme/"* "${output_dir}"/

find "${output_dir}"/ -type f -exec sed -i \
	-e "s/${lime}/${icons_color}/g" \
	-e "s/Archdroid-Lime/${OUTPUT_THEME_NAME}/g" \
	{} \; ;
echo done
