#!/bin/bash

podman run --privileged \
    -v $(pwd):/work \
    -i -t ruck \
