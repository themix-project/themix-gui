#!/usr/bin/env bash
set -ueo pipefail

if [[ -z "${DISPLAY:-}" ]] ; then
	# we need it as we're a GTK app:
	Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp 2>&1  &
	xvfb_pid="$!"

	clean_up() {
		echo -e "\n== Killing Xvfb..."
		kill ${xvfb_pid}
		echo "== Done."
	}
	trap clean_up EXIT SIGHUP SIGINT SIGTERM

	echo '== Started Xvfb'
	export DISPLAY=:99
	sleep 3
fi

export PYTHONWARNINGS='default,error:::oomox_gui[.*],error:::plugins[.*]'

echo '== Running on system python'
python3 --version

echo -e "\n== Running python compile:"
python3 -O -m compileall ./oomox_gui/ ./plugins/*/oomox_plugin.py | (grep -v -e '^Listing' -e '^Compiling' || true)
echo ':: python compile passed ::'

echo -e "\n== Running flake8:"
flake8 oomox_gui/ ./plugins/*/oomox_plugin.py
echo ':: flake8 passed ::'

echo -e "\n== Running pylint:"
#pylint --jobs="$(nproc)" oomox_gui ./plugins/*/oomox_plugin.py --score no
# @TODO: --jobs is broken at the moment: https://github.com/PyCQA/pylint/issues/374
pylint oomox_gui ./plugins/*/oomox_plugin.py --score no
echo ':: pylint passed ::'


if [[ "${SKIP_MYPY:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping mypy"
else
	echo -e "\n== Running mypy:"
	env MYPYPATH=./maintenance_scripts/mypy_stubs python -m mypy --warn-unused-ignores oomox_gui/plugin_api.py
	echo ':: mypy passed ::'
fi


if [[ "${SKIP_VULTURE:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping vulture"
else
	echo -e "\n== Running vulture:"
	vulture oomox_gui/ ./plugins/*/oomox_plugin.py \
		./maintenance_scripts/vulture_whitelist.py \
		--min-confidence=1 \
		--sort-by-size
	echo ':: vulture passed ::'
fi


if [[ "${SKIP_SHELLCHECK:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping shellcheck"
else
	echo -e "\n== Running shellcheck:"
	./maintenance_scripts/shellcheck.sh
fi


echo -e "\n"'$$ All checks have been passed successfully $$'
