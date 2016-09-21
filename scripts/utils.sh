#!/bin/bash

do_install() {
	local GTKDIR GTK320DIR GTKVER INSTALL_DIR
	INSTALL_DIR="$1"
	GTKDIR="${INSTALL_DIR}/gtk-3.0"
	GTK320DIR="${INSTALL_DIR}/gtk-3.20"

	install -dm755 "${INSTALL_DIR}"
	cp index.theme "${INSTALL_DIR}"

	for _DIR in "${GTKDIR}" "${GTK320DIR}"
	do
		GTKVER="${_DIR##*/}"

		cd src

		mkdir -p "${_DIR}"

		cp -rt "${INSTALL_DIR}" \
			gtk-2.0 metacity-1 openbox-3 xfce-notify-4.0 xfwm4 unity

		cp -t "${_DIR}" \
			"${GTKVER}/dist/gtk.css" \
			"${GTKVER}/dist/gtk-dark.css" \
			"${GTKVER}/gtk.gresource" \
			"${GTKVER}/thumbnail.png"

		cd -
	done
}


update_changes_file() {
	local LATEST_STABLE_RELEASE
	LATEST_STABLE_RELEASE=$(git describe --tags $(git rev-list --tags --max-count=1))

	[[ -f CHANGES ]] && mv CHANGES CHANGES.old

	{ git log \
		--pretty=format:"[%ai] %<(69,trunc) %s %><(15) %aN {%h}" \
		--cherry-pick "${LATEST_STABLE_RELEASE}...HEAD"; } > CHANGES

	[[ -f CHANGES.old ]] && cat CHANGES.old >> CHANGES && rm CHANGES.old

	git add CHANGES
	git commit -m 'RELEASE PREP :: Update CHANGES file.'
	git push
}



case $1 in
	changes)
		update_changes_file
		exit $?
	;;

	install)
		do_install "$2"
	;;

	*)
		exit 0
	;;
esac
