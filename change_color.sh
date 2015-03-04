#!/bin/bash

test -z "$1" &&
  echo "usage: $0 PRESET_NAME [OUTPUT_THEME_NAME]" &&
  exit 1

SRC_PATH=$(readlink -e $(dirname $0))
THEME=$1
OUTPUT_THEME_NAME="$2"

test -z "$OUTPUT_THEME_NAME" && OUTPUT_THEME_NAME=oomox-$THEME
DEST_PATH=~/.themes/"$OUTPUT_THEME_NAME"

PATHLIST=(
	'./openbox-3/'
	'./gtk-2.0/'
	'./gtk-3.0/'
	'./xfwm4/'
)


replace () {
	for FILEPATH in "${PATHLIST[@]}";
	do
		grep -lZR $1 $FILEPATH | xargs -0 -n 1 sed -i -e 's/'"$1"'/'"$2"'/g';
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

source $SRC_PATH/colors/$THEME.sh &&
source $SRC_PATH/current_colors.txt &&

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
