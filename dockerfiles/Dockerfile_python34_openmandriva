FROM openmandriva/3.0
WORKDIR /opt/oomox-build/

# App and test (xvfb, pylint) deps
RUN urpmi.update -a && \
    urpmi gtk+3.0 python-pip x11-server-xvfb psmisc \
        python-gobject python-gi-cairo gnome-tweak-tool \
        pango lib64gl1 lib64python-devel python-libxml2 python-notify adwaita-icon-theme
RUN pip install setuptools && \
    pip install pylint

COPY . /opt/oomox-build/
