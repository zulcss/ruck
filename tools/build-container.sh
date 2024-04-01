#!/bin/bash

# qemu-binfmt with non-native chroot
sudo apt update
sudo apt install qemu-user-static -y

docker build -t ruck docker
