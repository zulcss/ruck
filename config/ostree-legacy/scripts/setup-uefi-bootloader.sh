#!/bin/sh

# Based on original script from OStree upstream:
# https://github.com/ostreedev/ostree/blob/master/src/switchroot/switchroot.sh
# Copyright (C) 2013, 2016 Collabora Ltd
# Copyright (C) 2023 Wind River Systems, Inc.

set -eu

sysroot=${ROOTDIR}

osname=$1

bootconf=$sysroot/boot/loader/entries/ostree-1-${osname}.conf

if [ ! -f "$bootconf" ]; then
    echo "OStree setup is not available!"
    exit 1
fi

ostree=$(grep -o 'ostree=[/.[:alnum:]]\+' $bootconf)
ostree=${ostree#*=}
# Due symlink
ostree=$(realpath $sysroot$ostree)

mkdir -p $ostree/boot/efi

## /etc/machine-id must be writable to allow to work systemd-nspawn
# but original `machine-id` file must stay empty in build time.
touch /tmp/machine-id
mount --bind /tmp/machine-id $ostree/etc/machine-id

# NB: The native resolv.conf management is supported only from systemd v.232.
systemd-nspawn --resolv-conf=off -D $ostree systemd-machine-id-setup

# install EFI
systemd-nspawn \
  --resolv-conf=off \
  --bind $sysroot/boot:/boot \
  --bind $sysroot/boot/efi:/boot/efi \
  --bind $sysroot/ostree/deploy/${osname}/var:/var \
  -D $ostree bootctl --path=/boot/efi install

umount $ostree/etc/machine-id
rmdir $ostree/boot/efi

# Copy config, kernel and initrd
# Change the name of config to unify with patch added in T4469
rsync -Pav $sysroot/boot/ostree $sysroot/boot/efi/
mkdir $sysroot/boot/efi/loader/entries/
cp $bootconf $sysroot/boot/efi/loader/entries/ostree-0-1.conf
rm -f $sysroot/boot/efi/loader/loader.conf
