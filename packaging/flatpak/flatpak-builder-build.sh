#!/bin/sh
	#--skip-if-unchanged \
flatpak-builder \
	app-dir com.github.actionless.oomox.json \
	$@
