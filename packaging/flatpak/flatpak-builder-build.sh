#!/bin/sh
	#--skip-if-unchanged \
flatpak-builder \
	app-dir com.github.themix_project.Oomox.json \
	"$@"
