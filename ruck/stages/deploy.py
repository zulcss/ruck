"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck.stages.base import Base
from ruck import utils

SCHEMA = {
    "target": {"type": "string", "required": True},
    "image": {"type": "string", "required": True},
}


class DeployPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")

        self.rootfs = self.workspace.joinpath("rootfs")

    def run(self):
        """Deploy rootfs to an image."""
        self.logging.info("Deploying to image.")

        target = self.workspace.joinpath(self.config.get("target"))
        image = self.workspace.joinpath(self.config.get("image"))

        self.rootfs.mkdir(parents=True, exist_ok=True)

        self._mount(image)
        self._unpack(target)
        self._umount(image)

    def _unpack(self, target):
        self.logging.info(f"Unpacking {target}")
        utils.run_command(
            ["tar", "-C", self.rootfs, "-zxf", target, "--numeric-owner"]
        )

    def _mount(self, image):
        self.logging.info(f"Mounting {image} on {self.rootfs}.")
        utils.run_command(
            ["systemd-dissect", "-m", image, self.rootfs])

    def _umount(self, image):
        self.logging.info(f"Umounting {self.rootfs}.")
        utils.run_command(
            ["systemd-dissect", "-u", self.rootfs])
