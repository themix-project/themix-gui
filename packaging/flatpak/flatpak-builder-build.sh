#!/bin/sh
	#--skip-if-unchanged \
flatpak-builder \
	app-dir org.gtk.oomox.json \
	$@
