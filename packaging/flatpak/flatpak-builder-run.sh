#!/bin/sh
	#--own-name=com.github.themix-project.oomox
	#--system-own-name=com.github.themix-project.oomox
flatpak-builder \
	--env=GDK_SCALE="$GDK_SCALE" \
	--env=GDK_DPI_SCALE="$GDK_DPI_SCALE" \
	--run app-dir com.github.themix-project.oomox.json \
	"${1-oomox-gui}"
