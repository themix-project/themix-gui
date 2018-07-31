#!/bin/sh
	#--own-name=com.github.themix_project.Oomox
	#--system-own-name=com.github.themix_project.Oomox
flatpak-builder \
	--env=GDK_SCALE="$GDK_SCALE" \
	--env=GDK_DPI_SCALE="$GDK_DPI_SCALE" \
	--run app-dir com.github.themix_project.Oomox.json \
	"${1-oomox-gui}"
