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
        python3-click \
        python3-gi \
        dosfstools \
        systemd-container \
        ostree \
        debos \
        rsync \
        dosfstools \
        gir1.2-ostree-1.0 \
        git

COPY files/pip.conf /etc/pip.conf

RUN mkdir -p usr/src

