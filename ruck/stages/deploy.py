"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck import exceptions
from ruck.archive import unpack
from ruck.mount import mount, umount
from ruck.schema import validate
from ruck.stages.base import Base

SCHEMA = {
    "step": {"type": "string"},
    "options": {
        "type": "dict",
        "schema": {
            "source": {"type": "string", "required": True},
            "target": {"type": "string", "required": True},
        },
    }
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

        state = validate(self.config, SCHEMA)
        if not state:
            raise exceptions.ConfigError("Configuration is invalid.")

        target = self.workspace.joinpath(self.options.get("source"))
        if not target.exists():
            raise exceptions.COnfigError(f"{target} not found.")

        image = self.workspace.joinpath(self.options.get("target"))
        if not image.exists():
            raise exceptions.COnfigError(f"{image} not found.")

        self.rootfs.mkdir(parents=True, exist_ok=True)

        self.logging.info(f"Mounting {image} on {self.rootfs}.")
        mount(image, self.rootfs)

        # Unpack the tarball.
        unpack(target, self.rootfs)

        self.logging.info(f"Umounting {self.rootfs}.")
        umount(self.rootfs)
