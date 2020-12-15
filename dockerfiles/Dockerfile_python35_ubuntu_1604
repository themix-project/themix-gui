FROM library/ubuntu:xenial
WORKDIR /opt/oomox-build/

# App and test (xvfb, pylint) deps
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gtk+3.0 python3-gi dbus xvfb python3-pip psmisc python3-pystache python3-yaml && \
    dbus-uuidgen --ensure
RUN pip3 install -U setuptools pip && \
    pip3 install pylint~=2.5.3 flake8~=3.8.4

COPY . /opt/oomox-build/

# vim: set ft=dockerfile:
