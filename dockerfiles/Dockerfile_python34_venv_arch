FROM archlinux/base
WORKDIR /opt/oomox-build/

# App and test (xvfb, pylint) deps
RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm gtk3 python-gobject python-pylint xorg-server-xvfb

# python3.4 virtualenv deps
RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm python-virtualenv gobject-introspection && \
    pacman -S --needed --noconfirm git base-devel && \
    useradd -m user && \
    echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    sudo -u user bash -c "\
        git clone https://aur.archlinux.org/python34 /home/user/python34 && \
        cd /home/user/python34 && \
        makepkg --install --syncdeps --noconfirm"

COPY . /opt/oomox-build/
# customize test
RUN echo -e "#!/usr/bin/env bash\n \
    set -ueo pipefail ; \
    Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp & \
    echo '== Started Xvfb' ; \
    echo '== Running on system python' ; \
    python --version ; \
    export DISPLAY=:99 ; \
    sleep 3 ; \
    \
    virtualenv --system-site-packages -p python3.4 env34 ; \
    set +u ; \
    source env34/bin/activate ; \
    set -u ; \
    pip install pylint PyGObject ; \
    echo '== Running on python 3.4' ; \
    python --version ; \
    pylint oomox_gui ; \
    echo -n plugins/*/oomox_plugin.py | xargs -d ' ' -n 1 pylint ; \
    deactivate ; \
    \
    killall Xvfb \
" > /opt/oomox-build/maintenance_scripts/run_ci.sh
