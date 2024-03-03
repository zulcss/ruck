"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import hashlib
import logging
import shutil
import sys
import os
import pathlib

from ruck import exceptions
from ruck.ostree import Ostree
from ruck.archive import unpack
from ruck.stages.base import Base
from ruck import utils


class OstreeBase(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.ostree = Ostree(self.state)

        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")


class OstreeInitPlugin(OstreeBase):
    def run(self):
        self.logging.info("Creating ostree repository.")

        repo = pathlib.Path(self.options.get("repo"))
        mode = self.options.get("mode")

        if not repo.exists():
            utils.run_command(
                ["ostree", "init", "--repo", repo])

class OstreePrepPlugin(OstreeBase):
    def run(self):
        self.logging.info("Creating ostree repository.")

        repo = pathlib.Path(self.options.get("repo"))
        branch = self.options.get("branch")
        target = self.workspace.joinpath(self.options.get("target"))
        
        self.rootfs = self.workspace.joinpath("rootfs")
        if self.rootfs.exists():
            shutil.rmtree(self.rootfs)
        self.rootfs.mkdir(parents=True, exist_ok=True)
        unpack(target, self.rootfs)

        self.logging.info("Moving /etc to /usr/etc.")
        os.rename(
            self.rootfs.joinpath("etc"),
            self.rootfs.joinpath("usr/etc"))
        self.logging.info("Moving /var/lib/dpkg to /usr/share/dpkg/database")
        os.rename(
            self.rootfs.joinpath("var/lib/dpkg"),
            self.rootfs.joinpath("usr/share/dpkg/database"))

        self.logging.info("Clearing /var")
        shutil.rmtree(self.rootfs.joinpath("var"))
        self.rootfs.joinpath("var").mkdir(parents=True, exist_ok=True)

        self.logging.info("Installing kernel")
        for d in self.rootfs.glob("boot/vmlinuz-*"):
            kver = d.name.removeprefix("vmlinuz-")
        shutil.copy(
            self.rootfs.joinpath(f"boot/vmlinuz-{kver}"),
            self.rootfs.joinpath(f"usr/lib/modules/{kver}/vmlinuz")
        )
        self.logging.info("Installing ramdisk")
        shutil.copy(
            self.rootfs.joinpath(f"boot/initrd.img-{kver}"),
            self.rootfs.joinpath(f"usr/lib/modules/{kver}/initrd.img"))

        r = self.ostree.ostree_commit(
                self.rootfs,
                branch=branch,
                repo=repo,
                subject="Initial commit")

