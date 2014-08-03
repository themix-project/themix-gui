#!/bin/bash

test -z "$1" &&
  echo 'usage: ./change_color.sh PRESET_NAME [OUTPUT_THEME_NAME]' &&
  exit 1

SRC_PATH=$(readlink -e $(dirname $0))
OUTPUT_THEME_NAME="$2"

test -z "$OUTPUT_THEME_NAME" && OUTPUT_THEME_NAME=oomox_current
DEST_PATH=~/.themes/"$OUTPUT_THEME_NAME"

FILELIST=(
	'openbox-3/themerc'
	'gtk-2.0/gtkrc'
	'gtk-3.0/gtk.css'
)


replace () {
	for FILE in "${FILELIST[@]}";
	do
		sed -i -e 's/'"$1"'/'"$2"'/g' "$FILE";
	done;
}

test "$SRC_PATH" = "$DEST_PATH" && echo "can't do that" && exit 1 ||
(
  rm -r $DEST_PATH ;
  mkdir -p $DEST_PATH ;
  cp -r \
	  $SRC_PATH/index.theme \
	  $SRC_PATH/gtk-2.0 \
	  $SRC_PATH/gtk-3.0 \
	  $SRC_PATH/openbox-3 \
	$DEST_PATH
) &&

source ./colors/$1.sh &&

     OLD_BG=$(sed -n '1p' < current_colors.txt) &&
     OLD_FG=$(sed -n '2p' < current_colors.txt) &&
 OLD_SEL_BG=$(sed -n '3p' < current_colors.txt) &&
 OLD_SEL_FG=$(sed -n '4p' < current_colors.txt) &&
 OLD_TXT_BG=$(sed -n '5p' < current_colors.txt) &&
 OLD_TXT_FG=$(sed -n '6p' < current_colors.txt) &&
OLD_MENU_BG=$(sed -n '7p' < current_colors.txt) &&
OLD_MENU_FG=$(sed -n '8p' < current_colors.txt) &&
OLD_BTN_BG=$(sed -n '9p' < current_colors.txt) &&
OLD_BTN_FG=$(sed -n '10p' < current_colors.txt) &&

cd $DEST_PATH &&
replace $OLD_BG $BG &&
replace $OLD_FG $FG &&
replace $OLD_SEL_BG $SEL_BG &&
replace $OLD_SEL_FG $SEL_FG &&
replace $OLD_TXT_BG $TXT_BG &&
replace $OLD_TXT_FG $TXT_FG &&
replace $OLD_MENU_BG $MENU_BG &&
replace $OLD_MENU_FG $MENU_FG &&
replace $OLD_BTN_BG $BTN_BG &&
replace $OLD_BTN_FG $BTN_FG &&

exit 0
