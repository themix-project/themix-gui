#!/bin/sh
cd "$(dirname "$0")" &&
exec python3 -m oomox_gui.multi_export_cli "$@"
