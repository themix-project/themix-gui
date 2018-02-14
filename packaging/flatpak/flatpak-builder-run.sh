#!/bin/sh
	#--own-name=org.gtk.oomox
	#--system-own-name=org.gtk.oomox
flatpak-builder \
	--env=GDK_SCALE="$GDK_SCALE" \
	--env=GDK_DPI_SCALE="$GDK_DPI_SCALE" \
	--run app-dir org.gtk.oomox.json \
	"${1-oomox-gui}"
