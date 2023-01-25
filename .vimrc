"let g:ale_linters = { 'python': ['mypy', 'pylint', 'pylsp'], }
"let g:ale_linters_ignore = { 'python': ['pylsp'] }
let g:ale_linters = { 'python': ['ruff', 'pylsp', 'flake8', ], }
"let g:ale_python_vulture_options = ' ./maintenance_scripts/vulture_whitelist.py '
let g:ale_python_pylint_options = ' ./maintenance_scripts/gtk_init_for_pylint_sigh.py '
let $MYPYPATH .= './maintenance_scripts/mypy_stubs/'
autocmd VimEnter * :echo "local vimrc loaded! 😺"
