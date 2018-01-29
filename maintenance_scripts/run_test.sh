#!/usr/bin/env bash
set -ueo pipefail

Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp &
echo '== Started Xvfb'
echo '== Running on system python'
python3 --version
export DISPLAY=:99
sleep 3

pylint oomox_gui
echo -n plugins/*/oomox_plugin.py | xargs -d ' ' -n 1 pylint

killall Xvfb
