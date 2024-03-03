#!/bin/bash
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0

dir=$1
name=pablo

virt-install \
	--connect qemu:///system \
	--boot loader=/usr/share/ovmf/OVMF.fd \
	--machine q35 \
	--name pablo \
	--ram 8096 \
	--vcpus 4 \
	--os-variant debiantesting \
	--disk path=$dir \
	--noautoconsole \
	--check path_in_use=off \
	--import
