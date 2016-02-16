sed -i \
    -e 's/%MENU_BG%/333/g' \
	-e 's/%SEL_BG%/444/g' \
    -e 's/%BG%/000/g' \
	-e 's/%FG%/fff/g' \
    -e 's/%TXT_BG%/555/g' \
	-e 's/%TXT_FG%/666/g' \
	*.svg
