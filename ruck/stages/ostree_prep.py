"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import hashlib
import logging
import os
import pathlib
import shutil
import sys
import subprocess

from ruck.archive import unpack
from ruck import exceptions
from ruck.stages.base import OstreeBase
from ruck import utils

def ostree(*args, _input=None, **kwargs):
    args = list(args) + [f'--{k}={v}' for k, v in kwargs.items()]
    print("ostree " + " ".join(args), file=sys.stderr)
    subprocess.run(["ostree"] + args,
                   encoding="utf-8",
                   stdout=sys.stderr,
                   input=_input,
                   check=True)


class OstreePrepPlugin(OstreeBase):
    def preflight_check(self):
        self.logging.info("Creating ostree branch.")

        self.repo = self.config.options.repo
        self.branch = self.config.options.branch
        self.target = self.workspace.joinpath(self.config.options.target)

    def run(self):
        self.rootfs = self.workspace.joinpath("rootfs")
        if self.rootfs.exists():
            shutil.rmtree(self.rootfs)
        self.rootfs.mkdir(parents=True, exist_ok=True)
        unpack(self.target, self.rootfs)

        self._setup_boot(self.rootfs.joinpath("boot"),
                        self.rootfs.joinpath("usr/lib/ostree-boot"))
        self._convert_to_ostree()
        self.logging.info("Commiting to ostree")
        ostree("commit",
               str(self.rootfs),
               repo=self.repo,
               branch=self.branch,
               subject="Initial commit")

    def post_install(self):
        self.logging.info("Cleaning up")
        shutil.rmtree(self.rootfs)

    def _convert_to_ostree(self):
        CRUFT = ["boot/initrd.img", "boot/vmlinuz",
                 "initrd.img", "initrd.img.old",
                 "vmlinuz", "vmlinuz.old"]

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
            self.rootfs.joinpath("efi").mkdir(parents=True, exist_ok=True)
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

    def _setup_boot(self, bootdir, targetdir):
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
                                       "initrd.img", "initramfs")
                                   + "-" + csum))
