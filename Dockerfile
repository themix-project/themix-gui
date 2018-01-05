FROM base/archlinux
WORKDIR /opt/oomox-build/

RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm gtk3 python-gobject python-pylint xorg-server-xvfb

COPY . /opt/oomox-build/
RUN bash -c "\
    set -ueo pipefail ; \
    set -x ; \
    Xvfb :99 -ac -screen 0 1920x1080x16 -nolisten tcp & \
    echo '== Started Xvfb' ; \
    export DISPLAY=:99 ; \
    sleep 3 ; \
    pylint oomox_gui ; \
    echo -n plugins/*/oomox_plugin.py | xargs -d ' ' -n 1 pylint ; \
    killall Xvfb"
