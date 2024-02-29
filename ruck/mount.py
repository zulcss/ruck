"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from ruck import utils


def mount(image, rootfs):
    utils.run_command(
        ["systemd-dissect", "-M", image, rootfs])


def umount(rootfs):
    utils.run_command(
        ["systemd-dissect", "-U", rootfs])
