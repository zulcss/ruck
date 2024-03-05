"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import hashlib
import logging
import os
import pathlib
import shutil

from ruck.archive import unpack
from ruck.ostree import Ostree
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
        self.logging.info("Creating ostree branch.")

        self.repo = pathlib.Path(self.options.get("repo"))
        self.branch = self.options.get("branch")
        target = self.workspace.joinpath(self.options.get("target"))

        self.rootfs = self.workspace.joinpath("rootfs")
        if self.rootfs.exists():
            shutil.rmtree(self.rootfs)
        self.rootfs.mkdir(parents=True, exist_ok=True)
        unpack(target, self.rootfs)

        self.create_ostree()

    def create_ostree(self):
        self.setup_boot(self.rootfs.joinpath("boot"),
                        self.rootfs.joinpath("usr/lib/ostree-boot"))
        self.convert_to_ostree()
        self.logging.info("Commiting to ostree")
        self.ostree.ostree_commit(
            self.rootfs,
            branch=self.branch,
            repo=self.repo,
            subject="Initial commit")
    
    def convert_to_ostree(self):
        CRUFT = ["boot/initrd.img", "boot/vmlinuz",
                 "initrd.img", "initrd.img.old",
                 "vmlinuz", "vmlinuz.old"]
        assert self.rootfs is not None and self.rootfs != ""

        # Remove unecessary files
        self.logging.info("Removing unnecessary files.")
        for c in CRUFT:
            try:
                os.remove(self.rootfs.joinpath(c))
            except OSError:
                pass

        # Setup and split out etc
        self.logging.info("Moving /etc to /usr/etc.")
        shutil.move(self.rootfs.joinpath("etc"), self.rootfs.joinpath("usr"))

        self.logging.info("Setting up /ostree and /sysroot.")
        try:
            self.rootfs.joinpath("ostree").mkdir(parents=True, exist_ok=True)
            self.rootfs.joinpath("sysroot").mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        self.logging.info("Setting up symlinks.")
        TOPLEVEL_LINKS = {
            "media": "run/media",
            "mnt": "var/mnt",
            "opt": "var/opt",
            "ostree": "sysroot/ostree",
            "root": "var/roothome",
            "srv": "var/srv",
            "usr/local": "../var/usrlocal",
        }
        fd = os.open(self.rootfs, os.O_DIRECTORY)
        for l, t in TOPLEVEL_LINKS.items():
            shutil.rmtree(self.rootfs.joinpath(l))
            os.symlink(t, l, dir_fd=fd)

    def setup_boot(self, bootdir, targetdir):
        """Setup up the ostree bootdir"""
        vmlinuz = None
        initrd = None
        dtbs = None
        version = None

        try:
            os.mkdir(targetdir)
        except OSError:
            pass

        for item in os.listdir(bootdir):
            if item.startswith("vmlinuz"):
                assert vmlinuz is None
                vmlinuz = item
                _, version = item.split("-", 1)
            elif item.startswith("initrd.img") or item.startswith("initramfs"):
                assert initrd is None
                initrd = item
            elif item.startswith("dtbs"):
                assert dtbs is None
                dtbs = os.path.join(bootdir, item)
            else:
                # Move all other artifacts as is
                shutil.move(os.path.join(bootdir, item), targetdir)
        assert vmlinuz is not None

        m = hashlib.sha256()
        m.update(open(os.path.join(bootdir, vmlinuz), mode="rb").read())
        if initrd is not None:
            m.update(open(os.path.join(bootdir, initrd), "rb").read())

        csum = m.hexdigest()

        os.rename(os.path.join(bootdir, vmlinuz),
                  os.path.join(targetdir, vmlinuz + "-" + csum))

        if initrd is not None:
            os.rename(os.path.join(bootdir, initrd),
                      os.path.join(targetdir,
                                   initrd.replace(
                                       "initrd.img", "initramfs") + "-" + csum))
