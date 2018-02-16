#!/bin/sh
	#--own-name=com.github.actionless.oomox
	#--system-own-name=com.github.actionless.oomox
flatpak-builder \
	--env=GDK_SCALE="$GDK_SCALE" \
	--env=GDK_DPI_SCALE="$GDK_DPI_SCALE" \
	--run app-dir com.github.actionless.oomox.json \
	"${1-oomox-gui}"
