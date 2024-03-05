FROM debian:testing

RUN apt-get update && \
    apt-get install -y \
        mmdebstrap \
        dosfstools \
		systemd \
        systemd-boot \
        python3-pip \
        python3-yaml \
        python3-rich \
        python3-stevedore \
        python3-cerberus \
        python3-systemd \
        dosfstools \
        systemd-container \
        git

COPY files/pip.conf /etc/pip.conf

RUN mkdir -p usr/src

