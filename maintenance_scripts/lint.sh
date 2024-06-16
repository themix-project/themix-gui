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


FIX_MODE=0
CHECK_RUFF_RULES=0
while getopts fr name
do
   case $name in
   f)   FIX_MODE=1;;
   r)   CHECK_RUFF_RULES=1;;
   ?)   printf "Usage: %s: [-f] [TARGETS]\n" "$0"
	   echo "Arguments:"
	   echo "  -f	run in fix mode"
	   echo "  -r	check if ruff rules config up-to-date"
		 exit 2;;
   esac
done
shift $((OPTIND - 1))
printf "Remaining arguments are: %s\n$*"


PYTHON=python3
TARGET_MODULE='oomox_gui'
TARGETS=(
	'./oomox_gui/'
	./plugins/*/oomox_plugin.py
	./maintenance_scripts/*.py
)
if [[ -n "${1:-}" ]] ; then
	TARGETS=("$@")
fi


install_ruff() {
	if [[ ! -f "${APP_DIR}/env/bin/activate" ]] ; then
		"$PYTHON" -m venv "${APP_DIR}/env" --system-site-packages
		# shellcheck disable=SC1091
		. "${APP_DIR}/env/bin/activate"
		"$PYTHON" -m pip install ruff --upgrade
		deactivate
	fi
}
RUFF="${APP_DIR}/env/bin/ruff"


if [[ "$CHECK_RUFF_RULES" -eq 1 ]] ; then
	echo -e "\n== Checking Ruff rules up-to-date:"
	install_ruff
	"$APP_DIR"/env/bin/pip install -U ruff
	diff --color -u \
		<(awk '/select = \[/,/]/' pyproject.toml \
			| sed -e 's|", "|/|g' \
			| head -n -1 \
			| tail -n +2 \
			| tr -d '",#' \
			| awk '{print $1;}' \
			| sort) \
		<("$RUFF" linter \
			| awk '{print $1;}' \
			| sort)
elif [[ "$FIX_MODE" -eq 1 ]] ; then
	for file in $(flake8 "${TARGETS[@]}" 2>&1 | cut -d: -f1 | uniq) ; do
		autopep8 --in-place "$file"
	done
	"$RUFF" check --unsafe-fixes --fix "${TARGETS[@]}"
else
	export PYTHONWARNINGS='default,error:::'"$TARGET_MODULE"'[.*],error:::plugins[.*]'

	echo '== Running on system python'
	"$PYTHON" --version

	echo -e "\n== Running python compile:"
	"$PYTHON" -O -m compileall "${TARGETS[@]}" \
	| (\
		grep -v -e '^Listing' -e '^Compiling' || true \
	)
	echo ':: python compile passed ::'

	echo -e "\n== Running python import:"
	"$PYTHON" -c "import ${TARGET_MODULE}.main"
	echo ':: python import passed ::'

	echo -e "\n== Checking for non-Final globals:"
	./maintenance_scripts/get_non_final_expressions.sh "${TARGETS[@]}"
	echo ':: check passed ::'

	echo -e "\n== Checking for unreasonable global vars:"
	./maintenance_scripts/get_global_expressions.sh "${TARGETS[@]}"
	echo ':: check passed ::'

	if [[ "${SKIP_RUFF:-}" = "1" ]] ; then
		echo -e "\n!! WARNING !! skipping Ruff"
	else
		echo -e "\n== Ruff..."
		install_ruff
		"$RUFF" check "${TARGETS[@]}"
		echo ':: ruff passed ::'
	fi

	echo -e "\n== Running flake8:"
	flake8 "${TARGETS[@]}" 2>&1
	echo ':: flake8 passed ::'

	echo -e "\n== Running pylint:"
	pylint "${TARGETS[@]}" --score no 2>&1
	#| (
	#    grep -v \
	#        -e "^  warnings.warn($" \
	#        -e "^/usr/lib/python3.10/site-packages/" \
	#    || true \
	#)
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
			python -m mypy "$TARGET_MODULE"
			echo ':: mypy passed ::'
		#)
	fi


	if [[ "${SKIP_VULTURE:-}" = "1" ]] ; then
		echo -e "\n!! WARNING !! skipping vulture"
	else
		echo -e "\n== Running vulture:"
		vulture "${TARGETS[@]}" \
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
		echo ':: shellcheck passed ::'
		echo -e "\n== Running shellcheck on Makefile..."
		./maintenance_scripts/makefile_shellcheck.py
		echo ':: shellcheck makefile passed ::'
	fi

	echo -e "\n== Validate pyproject file..."
	(
		exit_code=0
		result=$(validate-pyproject pyproject.toml 2>&1) || exit_code=$?
		if [[ $exit_code -gt 0 ]] ; then
			echo "$result"
			exit $exit_code
		fi
	)
	echo ':: pyproject validation passed ::'
fi


echo -e "\n"'$$ All checks have been passed successfully $$'
