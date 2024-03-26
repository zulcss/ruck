"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging

from ruck import exceptions
from ruck.mount import mount
from ruck.mount import umount
from ruck.stages.base import Base
from ruck import utils

class BootloaderPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.rootfs = self.workspace.joinpath("rootfs")

    def preflight_check(self):
        self.logging.info("Configuring bootloader.")
        if self.config.options.image is None:
            raise exceptions.ConfigError(
                "Image is not specified.")
        self.image = self.workspace.joinpath(
            self.config.options.image)
        if not self.image.exists():
            raise exceptions.ConfigError("f{self.image} is not found.")

        if self.config.options.type is None:
            raise exceptions.ConfigError(
                "bootloader type is not specified."
            )
        if self.config.options.kernel_cmdline is None:
            raise exceptions.ConfigError(
                "Kernel cmdline is not speciied.")

    def run(self):
        """Install bootloader via bootctl."""
        if self.config.options.type == "sd-boot":
            self._install_sd_boot()

    def post_install(self):
        pass

    def _install_sd_boot(self):
        """Install bootloader via bootctl."""
        self.logging.info("Installing bootloader via bootctl")

        self.logging.info(f"Mounting {self.image} on {self.rootfs}")

        try:
            self.rootfs.mkdir(parents=True, exist_ok=True)
            mount(self.image, self.rootfs)

            self.logging.info("Installing bootloader")
            utils.run_chroot_command(
                ["bootctl", "install",
                 "--no-variables",
                 "--entry-token", "os-id"],
                 self.rootfs,
                 efi=self.rootfs)

            kver = self._install_kernel()
            self.logging.info(f"Unmounting {self.rootfs}.")

            self.logging.info(f"Insalling kernel {kver}.")
            utils.run_chroot_command(
                ["kernel-install", "add", kver, f"/boot/vmlinuz-{kver}"],
                self.rootfs, efi=self.rootfs)
        finally:
            umount(self.rootfs)

    def _install_kernel(self):
        """Configure kernel cmdine."""
        self.logging.info("Installing kernel and ramdisk.")

        # Should be only one kernel.
        for d in self.rootfs.glob("boot/vmlinuz-*"):
            kver = d.name.removeprefix("vmlinuz-")

        self.logging.info("Configuring kernel command-line.")
        cmdline = self.rootfs.joinpath("etc/kernel/cmdline")
        with open(cmdline, "w") as f:
            f.write(self.config.options.kernel_cmdline)

        return kver
