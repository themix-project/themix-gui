#!/bin/sh
sed -i \
         -e 's/rgb(0%,0%,0%)/#%BG%/g' \
         -e 's/rgb(100%,100%,100%)/#%FG%/g' \
    -e 's/rgb(50%,0%,0%)/#%MENU_BG%/g' \
     -e 's/rgb(0%,50%,0%)/#%SEL_BG%/g' \
 -e 's/rgb(0%,50.196078%,0%)/#%SEL_BG%/g' \
     -e 's/rgb(50%,0%,50%)/#%TXT_BG%/g' \
 -e 's/rgb(50.196078%,0%,50.196078%)/#%TXT_BG%/g' \
     -e 's/rgb(0%,0%,50%)/#%TXT_FG%/g' \
	*.svg
