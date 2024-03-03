"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging

from ruck.archive import unpack
from ruck.stages.base import Base

SCHEMA = {
    "target": {"type": "string"},
    "options": {
        "type": "dict",
        "schema": {
                "target": {"type": "string", "required": True}
            },
        }
}


class UnpackPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)
        self.options = self.config.get("options")

        self.rootfs = self.workspace.joinpath("rootfs")

    def run(self):
        self.logging.info(f"Unpacking {self.target}.")
        self.target = self.workspace.joinpath(self.options.get("target"))
        self.logging.info(f"Unpacking {self.rootfs}.")
        self.rootfs.mkdir(parents=True, exist_ok=True)
        unpack(self.target, self.rootfs)
