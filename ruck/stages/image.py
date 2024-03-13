"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shlex
import subprocess

from ruck import utils
from ruck.stages.base import Base


class ImagePlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace

        self.logging = logging.getLogger(__name__)
        self.options = self.config.get("options")
        self.images = self.options.get("image")
        self.partitions = self.options.get("partitions")
        self.filesystems = self.options.get("filesystems")

        self.image = None

    def run(self):
        self.create_image()
        self.create_label()
        self.create_partitions()
        self.create_filelsystems()

    def create_image(self):
        self.image = self.workspace.joinpath(self.images.get("name"))
        size = self.images.get("size")

        if self.image.exists():
            os.unlink(self.image)

        self.logging.info(f"Creating {self.image}")
        utils.run_command(["truncate", "-s", size, self.image])

    def create_label(self):
        label = self.images.get("label")
        if self.image.exists():
            # TODO(chuck): add msdos support
            if label not in ["gpt"]:
                self.logging.error(f"{label} is not a valid type.")
            utils.run_command(["parted", self.image, "--script", "mklabel", label])

    def create_partitions(self):
        """Use parted to create the partitions."""
        for index, part in enumerate(self.partitions, start=1):
            utils.run_command(
                [
                    "parted",
                    "-s",
                    self.image,
                    "--",
                    "mkpart",
                    part.get("name"),
                    part.get("start"),
                    part.get("end"),
                ]
            )
            flags = part.get("flags")
            if flags:
                for flag in flags:
                    cmd = f"parted -s {self.image} -- set {index} {flag} on"
                    utils.run_command(shlex.split(cmd))
            part_type = part.get("type")
            if part_type:
                cmd = f"sfdisk --part-type {self.image} {index} {part_type}"
                utils.run_command(shlex.split(cmd))

    def create_filelsystems(self):
        """Setup the image for the filesystems to be formatted."""
        self.logging.info("Setting up loopback device.")
        try:
            self.logging.info(f"Creating device map for {self.image}")
            loop = self.losetup()

            subprocess.run(["kpartx", "-a", loop], check=True)

            for index, part in enumerate(self.filesystems, start=1):
                fs = f"/dev/mapper/{os.path.basename(loop)}p{index}"
                if os.path.exists(fs):
                    self.mkfs(fs, part.get("fs"), part.get("label"), part.get("name"))

        finally:
            subprocess.run(["losetup", "-d", loop], check=True)
            subprocess.run(["kpartx", "-d", self.image], check=True)

    def mkfs(self, fs, fs_type, label, name):
        """Formatting the filesystem."""
        self.logging.info(f"Formatting filesystems for {name}.")

        if fs_type == "vfat":
            # vfat is a special case
            subprocess.run(["mkfs.vfat", "-F", "32", "-n", label, fs], check=True)
        else:
            subprocess.run(["mkfs", "-t", fs_type, "-L", label, fs], check=True)

    def losetup(self):
        """Find an empty loopt back device."""
        cmd = f"losetup --find --show {self.image}"
        return subprocess.run(
            shlex.split(cmd), encoding="utf8", check=True, stdout=subprocess.PIPE
        ).stdout.strip()
