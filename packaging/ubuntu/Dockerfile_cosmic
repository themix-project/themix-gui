FROM ubuntu:cosmic
WORKDIR /opt/oomox
RUN sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list && \
    apt update --allow-unauthenticated
CMD ["/bin/bash", "./packaging/ubuntu/create_ubuntu_package.sh", "control_1810", "--install"]
RUN apt update --allow-unauthenticated && \
	apt install -y make gettext fakeroot
#COPY . /opt/oomox/

# vim: set ft=dockerfile :
