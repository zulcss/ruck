#!/bin/bash

sudo podman run \
    --privileged \
    -v $(pwd):/work \
    -i -t ruck \
