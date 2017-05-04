#!/usr/bin/env bash

set -ue
SRC_PATH=$(readlink -f $(dirname $0))

darker () {
	"${SRC_PATH}/scripts/darker.sh" $@
}
mix () {
	"${SRC_PATH}/scripts/mix.sh" $@
}


print_usage() {
	echo "usage: $0 [-o OUTPUT_THEME_NAME] [-p PATH_LIST] [-m MAKE_OPTS] PRESET_NAME_OR_PATH"
	echo "examples:"
	echo "       $0 monovedek"
	echo "       $0 -o my-theme-name ./colors/retro/twg"
	echo "       $0 -o oomox-gnome-noble -p \"./gtk-2.0 ./gtk-3.0 ./gtk-3.20 ./Makefile\" gnome-noble"
	echo "       $0 -o oomox-gnome-noble -p \"./gtk-2.0 ./gtk-3.0 ./gtk-3.20 ./Makefile\" -m gtk320 gnome-noble"
	exit 1
}


while [[ $# > 0 ]]
do
	case ${1} in
		-p|--path-list)
			CUSTOM_PATHLIST="${2}"
			shift
		;;
		-o|--output)
			OUTPUT_THEME_NAME="${2}"
			shift
		;;
		-m|--make-opts)
			MAKE_OPTS="${2}"
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

PATHLIST=(
	'./src/openbox-3'
	'./src/assets'
	'./src/gtk-2.0'
	'./src/gtk-3.0'
	'./src/gtk-3.20'
	'./src/xfwm4'
	'./src/metacity-1'
	'./src/unity'
	'Makefile'
	'./src/index.theme'
	'./src/qt5ct_palette.conf'
)
if [ ! -z "${CUSTOM_PATHLIST:-}" ] ; then
	IFS=', ' read -r -a PATHLIST <<< "${CUSTOM_PATHLIST:-}"
fi

MAKE_GTK3=0
EXPORT_QT5CT=0
for FILEPATH in "${PATHLIST[@]}"; do
	if [[ ${FILEPATH} == *Makefile* ]] ;then
		MAKE_GTK3=1
	elif [[ ${FILEPATH} == *qt5ct* ]] ;then
		EXPORT_QT5CT=1
	fi
done
MAKE_OPTS="${MAKE_OPTS-all}"

if [[ ${THEME} == */* ]] || [[ ${THEME} == *.* ]] ; then
	source "$THEME"
	THEME=$(basename ${THEME})
else
	source "$SRC_PATH/colors/$THEME"
fi
HDR_BTN_BG=${HDR_BTN_BG-$BTN_BG}
HDR_BTN_FG=${HDR_BTN_FG-$BTN_FG}
WM_BORDER_FOCUS=${WM_BORDER_FOCUS-$MENU_BG}
WM_BORDER_UNFOCUS=${WM_BORDER_UNFOCUS-$MENU_BG}

GTK3_GENERATE_DARK=$(echo ${GTK3_GENERATE_DARK-True} | tr '[:upper:]' '[:lower:]')
GTK2_HIDPI=$(echo ${GTK2_HIDPI-False} | tr '[:upper:]' '[:lower:]')
UNITY_DEFAULT_LAUNCHER_STYLE=$(echo ${UNITY_DEFAULT_LAUNCHER_STYLE-False} | tr '[:upper:]' '[:lower:]')

SPACING=${SPACING-3}
GRADIENT=${GRADIENT-0}
ROUNDNESS=${ROUNDNESS-2}
ROUNDNESS_GTK2_HIDPI=$(( ${ROUNDNESS} * 2 ))

INACTIVE_FG=$(mix ${FG} ${BG} 0.75)
INACTIVE_MENU_FG=$(mix ${MENU_FG} ${MENU_BG} 0.75)
INACTIVE_TXT_FG=$(mix ${TXT_FG} ${TXT_BG} 0.75)

light_folder_base_fallback="$(darker ${SEL_BG} -10)"
medium_base_fallback="$(darker ${SEL_BG} 37)"
dark_stroke_fallback="$(darker ${SEL_BG} 50)"

ICONS_LIGHT_FOLDER="${ICONS_LIGHT_FOLDER-$light_folder_base_fallback}"
ICONS_LIGHT="${ICONS_LIGHT-$SEL_BG}"
ICONS_MEDIUM="${ICONS_MEDIUM-$medium_base_fallback}"
ICONS_DARK="${ICONS_DARK-$dark_stroke_fallback}"

CARET1_FG="${CARET1_FG-$TXT_FG}"
CARET2_FG="${CARET2_FG-$TXT_FG}"
CARET_SIZE="${CARET_SIZE-0.04}"

OUTPUT_THEME_NAME="${OUTPUT_THEME_NAME-oomox-$THEME}"
DEST_PATH="$HOME/.themes/${OUTPUT_THEME_NAME/\//-}"

test "$SRC_PATH" = "$DEST_PATH" && echo "can't do that" && exit 1


rm -r "$DEST_PATH" || true
mkdir -p "$DEST_PATH"
cp -r "$SRC_PATH/src/index.theme" "$DEST_PATH"
for FILEPATH in "${PATHLIST[@]}"; do
	cp -r "$SRC_PATH/$FILEPATH" "$DEST_PATH"
done


cd "$DEST_PATH"
for FILEPATH in "${PATHLIST[@]}"; do
	find $(echo "${FILEPATH}" | sed -e 's/src\///g' ) -type f -exec sed -i'' \
		-e 's/%BG%/'"$BG"'/g' \
		-e 's/%FG%/'"$FG"'/g' \
		-e 's/%SEL_BG%/'"$SEL_BG"'/g' \
		-e 's/%SEL_FG%/'"$SEL_FG"'/g' \
		-e 's/%TXT_BG%/'"$TXT_BG"'/g' \
		-e 's/%TXT_FG%/'"$TXT_FG"'/g' \
		-e 's/%MENU_BG%/'"$MENU_BG"'/g' \
		-e 's/%MENU_FG%/'"$MENU_FG"'/g' \
		-e 's/%BTN_BG%/'"$BTN_BG"'/g' \
		-e 's/%BTN_FG%/'"$BTN_FG"'/g' \
		-e 's/%HDR_BTN_BG%/'"$HDR_BTN_BG"'/g' \
		-e 's/%HDR_BTN_FG%/'"$HDR_BTN_FG"'/g' \
		-e 's/%WM_BORDER_FOCUS%/'"$WM_BORDER_FOCUS"'/g' \
		-e 's/%WM_BORDER_UNFOCUS%/'"$WM_BORDER_UNFOCUS"'/g' \
		-e 's/%ROUNDNESS%/'"$ROUNDNESS"'/g' \
		-e 's/%ROUNDNESS_GTK2_HIDPI%/'"$ROUNDNESS_GTK2_HIDPI"'/g' \
		-e 's/%SPACING%/'"$SPACING"'/g' \
		-e 's/%GRADIENT%/'"$GRADIENT"'/g' \
		-e 's/%INACTIVE_FG%/'"$INACTIVE_FG"'/g' \
		-e 's/%INACTIVE_TXT_FG%/'"$INACTIVE_TXT_FG"'/g' \
		-e 's/%INACTIVE_MENU_FG%/'"$INACTIVE_MENU_FG"'/g' \
		-e 's/%ICONS_DARK%/'"$ICONS_DARK"'/g' \
		-e 's/%ICONS_MEDIUM%/'"$ICONS_MEDIUM"'/g' \
		-e 's/%ICONS_LIGHT%/'"$ICONS_LIGHT"'/g' \
		-e 's/%ICONS_LIGHT_FOLDER%/'"$ICONS_LIGHT_FOLDER"'/g' \
		-e 's/%OUTPUT_THEME_NAME%/'"$OUTPUT_THEME_NAME"'/g' \
		-e 's/%CARET1_FG%/'"$CARET1_FG"'/g' \
		-e 's/%CARET2_FG%/'"$CARET2_FG"'/g' \
		-e 's/%CARET_SIZE%/'"$CARET_SIZE"'/g' \
		{} \; ;
done

if [[ ${GTK3_GENERATE_DARK} != "true" ]] ; then
	if [[ -f ./gtk-3.0/scss/gtk-dark.scss ]] ; then
		rm ./gtk-3.0/scss/gtk-dark.scss
	fi
	if [[ -f ./gtk-3.20/scss/gtk-dark.scss ]] ; then
		rm ./gtk-3.20/scss/gtk-dark.scss
	fi
fi
if [[ ${GTK2_HIDPI} == "true" ]] ; then
	mv ./gtk-2.0/gtkrc.hidpi ./gtk-2.0/gtkrc
fi
if [[ ${EXPORT_QT5CT} = 1 ]] ; then
	config_home=${XDG_CONFIG_HOME:-}
	if [[ -z "${config_home}" ]] ; then
		config_home="${HOME}/.config"
	fi
	qt5ct_colors_dir="${config_home}/qt5ct/colors/"
	test -d ${qt5ct_colors_dir} || mkdir -p ${qt5ct_colors_dir}
	mv ./qt5ct_palette.conf "${qt5ct_colors_dir}/${OUTPUT_THEME_NAME}.conf"
fi
if [[ ${UNITY_DEFAULT_LAUNCHER_STYLE} == "true" ]] ; then
	rm ./unity/launcher*.svg
fi

if [[ ${MAKE_GTK3} = 1 ]]; then
	make "${MAKE_OPTS}"
fi

exit 0
