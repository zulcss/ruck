#!/bin/bash

docker run \
     -i -t --privileged \
     -v $(pwd):/usr/src \
     -v $(pwd)/data:/var/tmp/ruck \
     -v /dev:/dev \
     -v /run:/run \
     -v /sys:/sys \
     -v /var/tmp:/var/tmp \
    -i -t ruck \
