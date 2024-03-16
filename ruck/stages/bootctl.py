"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck import exceptions
from ruck.mount import mount
from ruck.mount import umount
from ruck.schema import validate
from ruck.stages.base import Base
from ruck import utils

SCHEMA = {
    "step": {"type": "string"},
    "options": {
        "type": "dict",
        "schema": {
                "image": {"type": "string"},
                "kernel_cmdline": {"type": "string"},
            },
        },
}


class SDBootPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")

        self.rootfs = self.workspace.joinpath("rootfs")

    def run(self):
        """Install bootloader via bootctl."""
        self.logging.info("Configuring systemd-boot.")

        state = validate(self.config, SCHEMA)
        if not state:
            raise exceptions.ConfigError("Configuration is invalid.")

        self.image = self.workspace.joinpath(self.options.get("image"))
        if not self.image.exists():
            raise exceptions.ConfigError("f{self.image} is not found.")

        self.rootfs.mkdir(parents=True, exist_ok=True)
        self.logging.info(f"Mounting {self.image} on {self.rootfs}")

        mount(self.image, self.rootfs)

        self.logging.info("Installing bootloader")
        utils.run_chroot(
            ["bootctl", "install",
             "--no-variables",
             "--entry-token", "os-id"],
            self.rootfs,
            efi=self.rootfs)

        kver = self.install_kernel()
        self.logging.info(f"Unmounting {self.rootfs}.")

        self.logging.info(f"Installing kernel {kver}.")
        utils.run_chroot(
            ["kernel-install", "add", kver, f"/boot/vmlinuz-{kver}"],
            self.rootfs, efi=self.rootfs)
        umount(self.rootfs)

    def install_kernel(self):
        """Configure kernel cmdine."""
        self.logging.info("Installing kernel and ramdisk.")

        # Should be only one kernel.
        for d in self.rootfs.glob("boot/vmlinuz-*"):
            kver = d.name.removeprefix("vmlinuz-")

        self.logging.info("Cconfiguring kernel command-line.")
        cmdline = self.rootfs.joinpath("etc/kernel/cmdline")
        with open(cmdline, "w") as f:
            f.write(self.options.get("kernel_cmdline"))

        return kver
