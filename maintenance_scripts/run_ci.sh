#!/usr/bin/env bash
set -ueo pipefail

Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp &
xvfb_pid="$!"

clean_up() {
	kill ${xvfb_pid}
}
trap clean_up EXIT SIGHUP SIGINT SIGTERM

echo '== Started Xvfb'
echo '== Running on system python'
python3 --version
export DISPLAY=:99
sleep 3

echo -e "\n== Running pylint:"
pylint oomox_gui ./plugins/*/oomox_plugin.py --score no &&
echo ':: pylint passed ::'

if [[ "${NO_SHELLCHECK:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping shellcheck"
else
	echo -e "\n== Running shellcheck:"
	./maintenance_scripts/shellcheck.sh
fi
