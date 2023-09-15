#!/usr/bin/env bash
set -ueo pipefail

script_dir=$(readlink -e "$(dirname "${0}")")
APP_DIR="$(readlink -e "${script_dir}"/..)"

if [[ -z "${DISPLAY:-}" ]] ; then
	# we need it as we're a GTK app:
	Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp 2>&1  &
	xvfb_pid="$!"

	clean_up() {
		echo -e "\n== Killing Xvfb..."
		kill "$xvfb_pid"
		echo "== Done."
	}
	trap clean_up EXIT SIGHUP SIGINT SIGTERM

	echo '== Started Xvfb'
	export DISPLAY=:99
	sleep 3
fi

PYTHON=python3

FIX_MODE=0
while getopts f name
do
   case $name in
   f)   FIX_MODE=1;;
   ?)   printf "Usage: %s: [-f] [TARGETS]\n" "$0"
	   echo "Arguments:"
	   echo "  -f	run in fix mode"
		 exit 2;;
   esac
done
shift $((OPTIND - 1))
printf "Remaining arguments are: %s\n$*"

export PYTHONWARNINGS='default,error:::oomox_gui[.*],error:::plugins[.*]'
TARGETS=(
	'oomox_gui'
	./plugins/*/oomox_plugin.py
	./maintenance_scripts/*.py
)

echo '== Running on system python'
python3 --version

echo -e "\n== Running python compile:"
python3 -O -m compileall ./oomox_gui/ ./plugins/*/oomox_plugin.py | (grep -v -e '^Listing' -e '^Compiling' || true)
echo ':: python compile passed ::'

echo -e "\n== Running python import:"
python3 -c "import oomox_gui.main"
echo ':: python import passed ::'

echo -e "\n== Checking for non-Final globals:"
./maintenance_scripts/get_non_final_expressions.sh
echo ':: check passed ::'

if [[ "${SKIP_RUFF:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping Ruff"
else
	echo -e "\n== Running Ruff:"
	if [[ ! -f "${APP_DIR}/env/bin/activate" ]] ; then
		"$PYTHON" -m venv "${APP_DIR}/env" --system-site-packages
		# shellcheck disable=SC1091
		. "${APP_DIR}/env/bin/activate"
		"$PYTHON" -m pip install ruff --upgrade
		deactivate
	fi
	if [[ "$FIX_MODE" -eq 1 ]] ; then
		"${APP_DIR}/env/bin/ruff" --fix "${TARGETS[@]}" || true
	else
		"${APP_DIR}/env/bin/ruff" "${TARGETS[@]}"
	fi
fi

echo -e "\n== Running flake8:"
if [[ "$FIX_MODE" -eq 1 ]] ; then
	for file in $(flake8 "${TARGETS[@]}" 2>&1 | cut -d: -f1 | uniq) ; do
		autopep8 --in-place "$file"
	done
else
	flake8 "${TARGETS[@]}" 2>&1 \
	| (
		grep -v \
			-e "^  warnings.warn($" \
			-e "^/usr/lib/python3.10/site-packages/" \
		|| true \
	)
fi

echo ':: flake8 passed ::'

if [[ "$FIX_MODE" -eq 1 ]] ; then
	exit 0
fi

echo -e "\n== Running pylint:"
#pylint --jobs="$(nproc)" oomox_gui ./plugins/*/oomox_plugin.py --score no
# @TODO: --jobs is broken at the moment: https://github.com/PyCQA/pylint/issues/374
pylint oomox_gui ./plugins/*/oomox_plugin.py --score no 2>&1 \
| (
	grep -v \
		-e "^  warnings.warn($" \
		-e "^/usr/lib/python3.10/site-packages/" \
	|| true \
)
echo ':: pylint passed ::'


if [[ "${SKIP_MYPY:-}" = "1" ]] ; then
	echo -e "\n!! WARNING !! skipping mypy"
else
	#python -m venv mypy_venv --system-site-packages
	#(
	#    # shellcheck disable=SC1091
	#    . ./mypy_venv/bin/activate
	#    python -m pip install types-Pillow
		echo -e "\n== Running mypy:"
		python -m mypy oomox_gui
		echo ':: mypy passed ::'
	#)
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
	echo -e "\n== Running shellcheck on Makefile..."
	./maintenance_scripts/makefile_shellcheck.py
fi


echo -e "\n"'$$ All checks have been passed successfully $$'
