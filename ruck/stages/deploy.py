"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck.archive import unpack
from ruck import exceptions
from ruck.mount import mount
from ruck.mount import umount
from ruck.stages.base import Base


class DeployPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.rootfs = self.workspace.joinpath("rootfs")

    def preflight_check(self):
        """Deploy rootfs to an image."""
        self.logging.info("Deploying to image.")

        self.target = self.workspace.joinpath(self.config.options.source)
        if not self.target.exists():
            raise exceptions.ConfigError(f"{self.target} not found.")

        self.image = self.workspace.joinpath(self.config.options.target)
        if not self.image.exists():
            raise exceptions.ConfigError(f"{self.image} not found.")

    def run(self):
        self.logging.info("Deploying to image.")
        try:
            self.rootfs.mkdir(parents=True, exist_ok=True)

            self.logging.info(f"Mounting {self.image} on {self.rootfs}.")
            mount(self.image, self.rootfs)

            # Unpack the tarball.
            unpack(self.target, self.rootfs)
        finally:
            self.logging.info(f"Umounting {self.rootfs}.")
            umount(self.rootfs)

    def post_install(self):
        pass
