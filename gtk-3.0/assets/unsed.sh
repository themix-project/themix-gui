sed -i \
    -e 's/333/%MENU_BG%/g' \
	-e 's/444/%SEL_BG%/g' \
    -e 's/000/%BG%/g' \
	-e 's/fff/%FG%/g' \
    -e 's/555/%TXT_BG%/g' \
	-e 's/666/%TXT_FG%/g' \
	*.svg
