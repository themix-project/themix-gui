#!/bin/bash

test -z "$1" &&
 echo 'usage: ./change_color.sh PRESET_NAME' &&
 exit 1
 #echo 'example1: ./change_color.sh 222222 eeeeec 3e2f4f 888888 000000' &&
 #echo 'example2: ./change_color.sh 777777 111111 ff3377 999999 222222' &&
 #echo '333333 eeeeec 5e468c 888888 000000' &&
 #echo '555555 dddddb 5e468c 888888 000000' &&
 #echo 'NobleDark: ./change_color.sh 3c3c3c d4d4d4 75507b 4c4c4c d4d4d4' &&

SRC_PATH=./
DEST_PATH=~/.themes/ncc_current
####
rm -r $DEST_PATH
cp -r $SRC_PATH $DEST_PATH
####

source ./colors/$1.sh

OLD_BG=$(sed -n '1p' < current_colors.txt)
OLD_FG=$(sed -n '2p' < current_colors.txt)
OLD_SEL=$(sed -n '3p' < current_colors.txt)
OLD_TXT_BG=$(sed -n '4p' < current_colors.txt)
OLD_TXT_FG=$(sed -n '5p' < current_colors.txt)
OLD_MENU_BG=$(sed -n '6p' < current_colors.txt)
OLD_MENU_FG=$(sed -n '7p' < current_colors.txt)

cd $DEST_PATH
for FILE in $(find -type f); do
	#echo $FILE
	sed -i "s/#$OLD_BG/#$BG/g" "$FILE"
	sed -i "s/#$OLD_FG/#$FG/g" "$FILE"
	sed -i "s/#$OLD_SEL/#$SEL/g" "$FILE"
	sed -i "s/#$OLD_TXT_BG/#$TXT_BG/g" "$FILE"
	sed -i "s/#$OLD_TXT_FG/#$TXT_FG/g" "$FILE"
	sed -i "s/#$OLD_MENU_BG/#$MENU_BG/g" "$FILE"
	sed -i "s/#$OLD_MENU_FG/#$MENU_FG/g" "$FILE"
done

#echo $BG > current_colors.txt
#echo $FG >> current_colors.txt
#echo $SEL >> current_colors.txt
#echo $TXT_BG >> current_colors.txt
#echo $TXT_FG >> current_colors.txt
#echo $MENU_BG >> current_colors.txt
#echo $MENU_FG >> current_colors.txt

