FROM debian:testing

RUN apt-get update && \
    apt-get install -y mmdebstrap \
		       systemd \
		       python3-pip \
		       python3-yaml \
		       git

COPY files/pip.conf /etc/pip.conf

RUN mkdir -p usr/src

