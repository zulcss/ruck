"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shlex
import subprocess

from ruck.stages.base import Base
from ruck import utils


class PartedPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace

        self.logging = logging.getLogger(__name__)

        self.image = None

    def preflight_check(self):
        self.images = self.config.options.image
        self.partitions = self.config.options.partitions
        self.filesystems = self.config.options.filesystems

    def run(self):
        self._create_image()
        self._create_label()
        self._create_partitions()
        self._create_filesystems()

    def post_install(self):
        pass

    def _create_image(self):
        """Create a raw disk image."""
        self.image = self.workspace.joinpath(self.images.name)
        size = self.images.size

        if self.image.exists():
            self.logging.info(f"Found previous image, removing {self.image}")
            os.unlink(self.image)

        self.logging.info(f"Creating {self.image}")
        utils.run_command(["truncate", "-s", size, self.image])

    def _create_label(self):
        """Create a GPT label for the disk."""
        label = self.images.label
        if self.image.exists():
            # TODO(chuck): add msdos support
            if label not in ["gpt"]:
                self.logging.error(f"{label} is not a valid type.")

            self.logging.info(f"Creating GPT label for {self.image}.")
            utils.run_command(
                ["parted", self.image, "--script", "mklabel", label])

    def _create_partitions(self):
        """Use parted to create the partitions."""
        for index, part in enumerate(self.partitions, start=1):
            self.logging.info(f"Creating parttion for {part.name}.")
            (out, err) = utils.run_command(
                ["parted", "-s", self.image, "--", "mkpart", part.name,
                 part.start, part.end])

            self.logging.info(f"Setting partition type(s) for {part.name}.")
            for flag in part.flags:
                cmd = f"parted -s {self.image} -- set {index} {flag} on"
                utils.run_command(shlex.split(cmd))

    def _create_filesystems(self):
        """Setup the image for the filesystems to be formatted."""
        self.logging.info(f"Setting up loopback device for {self.image}.")
        try:
            self.logging.info(f"Creating device map for {self.image}")
            loop = self.losetup()

            for index, part in enumerate(self.filesystems, start=1):
                fs = f"/dev/{os.path.basename(loop)}p{index}"
                if os.path.exists(fs):
                    self._mkfs(fs,
                               part.fs,
                               part.label,
                               part.name)

        finally:
            subprocess.run(["losetup", "-d", loop], check=True)

    def _mkfs(self, fs, fs_type, label, name):
        """Formatting the filesystem."""
        self.logging.info(f"Formatting filesystems for {name}.")

        if fs_type == "vfat":
            # vfat is a special case
            subprocess.run(
                ["mkfs.vfat", "-F", "32", "-n", label, fs],
                check=True)
        else:
            subprocess.run(
                ["mkfs", "-t", fs_type, "-L", label, fs], check=True)

    def losetup(self):
        """Find an empty loopt back device."""
        cmd = f"losetup -P  --find --show {self.image}"
        return subprocess.run(shlex.split(cmd),
                              encoding="utf8",
                              check=True,
                              stdout=subprocess.PIPE).stdout.strip()
