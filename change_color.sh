#!/bin/bash

test -z "$1" &&
  echo 'usage: ./change_color.sh PRESET_NAME' &&
  exit 1

SRC_PATH=./
DEST_PATH=~/.themes/ncc_current

rm -r $DEST_PATH
cp -r $SRC_PATH $DEST_PATH

source ./colors/$1.sh

     OLD_BG=$(sed -n '1p' < current_colors.txt)
     OLD_FG=$(sed -n '2p' < current_colors.txt)
    OLD_SEL=$(sed -n '3p' < current_colors.txt)
 OLD_TXT_BG=$(sed -n '4p' < current_colors.txt)
 OLD_TXT_FG=$(sed -n '5p' < current_colors.txt)
OLD_MENU_BG=$(sed -n '6p' < current_colors.txt)
OLD_MENU_FG=$(sed -n '7p' < current_colors.txt)

replace () {
  grep -lZR $1 * | xargs -0 -n 1 sed -i -e 's/'"$2"'/'"$3"'/g'
}

cd $DEST_PATH &&
replace $OLD_BG $OLD_BG $BG &&
replace $OLD_FG $OLD_FG $FG &&
replace $OLD_SEL $OLD_SEL $SEL &&
replace $OLD_TXT_BG $OLD_TXT_BG $TXT_BG &&
replace $OLD_TXT_FG $OLD_TXT_FG $TXT_FG &&
replace $OLD_MENU_BG $OLD_MENU_BG $MENU_BG &&
replace $OLD_MENU_FG $OLD_MENU_FG $MENU_FG &&

exit 0
