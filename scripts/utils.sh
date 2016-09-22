#!/bin/bash

do_install() {
	local GTKDIR GTK320DIR GTKVER INSTALL_DIR
	INSTALL_DIR="$1"
	GTKDIR="${INSTALL_DIR}/gtk-3.0"
	GTK320DIR="${INSTALL_DIR}/gtk-3.20"

	install -dm755 "${INSTALL_DIR}"

	cd src

	cp index.theme "${INSTALL_DIR}"

	for _DIR in "${GTKDIR}" "${GTK320DIR}"
	do
		GTKVER="${_DIR##*/}"

		mkdir "${_DIR}"

		cp --preserve=links -rt "${INSTALL_DIR}" \
			assets gtk-2.0 metacity-1 openbox-3 xfce-notify-4.0 xfwm4 unity

		cp --preserve=links -t "${_DIR}" \
			"${GTKVER}/gtk.css" \
			"${GTKVER}/gtk-dark.css" \
			"${GTKVER}/gtk.gresource" \
			"${GTKVER}/thumbnail.png"

		cd "${_DIR}"
		ln -sr ../assets assets
		cd -
	done
}


output_changes_file_version_marker() {

	line() {
		dashes="$(printf '%0.s-' $(seq 1 13))"
		echo "${dashes}>>>> $1 <<<<${dashes}"
	}

	tag_line="$(line $1)"

	echo "-${tag_line}${tag_line}${tag_line}-"
}


update_changes_file() {
	local LATEST_STABLE_RELEASE
	LATEST_STABLE_RELEASE=$(git describe --tags $(git rev-list --tags --max-count=1))

	[[ -f CHANGES ]] && mv CHANGES CHANGES.old

	output_changes_file_version_marker "${LATEST_STABLE_RELEASE}" > CHANGES

	{ git log \
		--pretty=format:"[%ai] %<(69,trunc) %s %><(15) %aN {%h}" \
		--cherry-pick "${LATEST_STABLE_RELEASE}...HEAD"; } >> CHANGES


	[[ -f CHANGES.old ]] && echo "" >> CHANGES && cat CHANGES.old >> CHANGES && rm CHANGES.old

	#git add CHANGES
	#git commit -m 'RELEASE PREP :: Update CHANGES file.'
	#git push
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
