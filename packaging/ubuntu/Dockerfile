FROM ubuntu:zesty
WORKDIR /opt/oomox
CMD ["/bin/bash", "./packaging/ubuntu/create_ubuntu_package.sh"]
RUN apt update && apt install -y make gettext
COPY . /opt/oomox/
