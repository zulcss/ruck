"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck import utils

log = logging.getLogger(__name__)


def unpack(archive, rootfs):
    log.info(f"Unpaking {archive}.")
    utils.run_command(
        ["tar", "-C", rootfs, "-zxf", archive, "--numeric-owner"]
    )
