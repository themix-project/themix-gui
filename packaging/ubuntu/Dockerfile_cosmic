FROM ubuntu:cosmic
WORKDIR /opt/oomox
CMD ["/bin/bash", "./packaging/ubuntu/create_ubuntu_package.sh", "control_1810"]
RUN apt update && apt install -y make gettext
COPY . /opt/oomox/
