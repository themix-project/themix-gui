#!/usr/bin/env bash
set -ueo pipefail

(
	Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp 2>&1 \
	| grep -v -e '^>' -e 'xkbcomp'
) &
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

echo -e "\n== Running python compile:"
python3 -O -m compileall ./oomox_gui/ ./plugins/*/oomox_plugin.py | (grep -v -e '^Listing' -e '^Compiling' || true)
echo ':: python compile passed ::'

echo -e "\n== Running pylint:"
pylint oomox_gui ./plugins/*/oomox_plugin.py --score no
echo ':: pylint passed ::'


if [[ "${SKIP_MYPY:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping mypy"
else
	echo -e "\n== Running mypy:"
	env MYPYPATH=./maintenance_scripts/mypy_stubs mypy oomox_gui/plugin_api.py
	echo ':: mypy passed ::'
fi


if [[ "${SKIP_SHELLCHECK:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping shellcheck"
else
	echo -e "\n== Running shellcheck:"
	./maintenance_scripts/shellcheck.sh
fi
