#!/usr/bin/env bash
set -ueo pipefail

Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp &
xvfb_pid=$!

clean_up() {
	kill ${xvfb_pid}
}
trap clean_up EXIT SIGHUP SIGINT SIGTERM

echo '== Started Xvfb'
echo '== Running on system python'
python3 --version
export DISPLAY=:99
sleep 3

echo -e "\n== Checking main app:"
pylint oomox_gui
for plugin in ./plugins/*/oomox_plugin.py ; do
	echo -e "\n== Checking plugin ${plugin}:"
	pylint $plugin
done
