#!/bin/bash

test -z "$1" &&
  echo "usage: $0 PRESET_NAME [OUTPUT_THEME_NAME]" &&
  exit 1

SRC_PATH=$(readlink -e $(dirname $0))
THEME=$1
OUTPUT_THEME_NAME="$2"

test -z "$OUTPUT_THEME_NAME" && OUTPUT_THEME_NAME=oomox-$THEME
DEST_PATH=~/.themes/${OUTPUT_THEME_NAME/\//-}

PATHLIST=(
	'./openbox-3/'
	'./gtk-2.0/'
	'./gtk-3.0/'
	'./xfwm4/'
)


test "$SRC_PATH" = "$DEST_PATH" && echo "can't do that" && exit 1 ||
(
  rm -r $DEST_PATH ;
  mkdir -p $DEST_PATH ;
  cp -r $SRC_PATH/index.theme $DEST_PATH
  for FILEPATH in "${PATHLIST[@]}";
  do
	cp -r $SRC_PATH/$FILEPATH $DEST_PATH
  done;
) &&

source $SRC_PATH/colors/$THEME.sh &&
source $SRC_PATH/current_colors.txt &&

cd $DEST_PATH &&
for FILEPATH in "${PATHLIST[@]}";
do
	find $FILEPATH -type f -exec sed -i \
		-e 's/'"$OLD_BG"'/'"$BG"'/g' \
		-e 's/'"$OLD_FG"'/'"$FG"'/g' \
		-e 's/'"$OLD_SEL_BG"'/'"$SEL_BG"'/g' \
		-e 's/'"$OLD_SEL_FG"'/'"$SEL_FG"'/g' \
		-e 's/'"$OLD_TXT_BG"'/'"$TXT_BG"'/g' \
		-e 's/'"$OLD_TXT_FG"'/'"$TXT_FG"'/g' \
		-e 's/'"$OLD_MENU_BG"'/'"$MENU_BG"'/g' \
		-e 's/'"$OLD_MENU_FG"'/'"$MENU_FG"'/g' \
		-e 's/'"$OLD_BTN_BG"'/'"$BTN_BG"'/g' \
		-e 's/'"$OLD_BTN_FG"'/'"$BTN_FG"'/g' \
		{} \; ;
done;

exit 0
