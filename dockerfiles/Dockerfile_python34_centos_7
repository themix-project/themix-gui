FROM centos:7.5.1804
WORKDIR /opt/oomox-build/

# App and test (xvfb, pylint) deps
RUN yum-config-manager --enable extras && \
    yum install -y epel-release && \
    yum upgrade -y && \
    yum install -y gtk3 xorg-x11-server-Xvfb psmisc \
        cairo-devel cairo-gobject-devel gobject-introspection-devel gcc \
        python34-devel python34-pip python34-gobject python34-PyYAML && \
    dbus-uuidgen --ensure
RUN ln -s /usr/bin/python3.4 /usr/bin/python3
RUN python3 -m pip install -U setuptools pip && \
    python3 -m pip install -U pylint flake8 PyGObject

COPY . /opt/oomox-build/

# vim: set ft=dockerfile:
