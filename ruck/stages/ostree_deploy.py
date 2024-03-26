"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import shutil

from ruck import exceptions
from ruck.mount import mount
from ruck.mount import umount
from ruck.stages.base import OstreeBase
from ruck import utils


class OstreeDeployPlugin(OstreeBase):
    def preflight_check(self):
        self. repo = self.config.options.repo
        self.branch = self.config.options.branch
        self.image = self.workspace.joinpath(self.config.options.image)
        self.kernel_args = self.config.options.kernel_args

        self.rootfs = self.workspace.joinpath("rootfs")
        if self.rootfs.exists():
            shutil.rmtree(self.rootfs)
        if not self.image.exists():
            raise exceptions.ConfigError(f"Unable to find {self.image}.")

    def run(self):
        self.logging.info("Deploying ostree repository.")

        self.logging.info(f"Mounting {self.image} on {self.rootfs}")
        try:
            mount(self.image, self.rootfs)

            ostree_repo = self.rootfs.joinpath("ostree/repo")
            self.logging.info(f"Creating {ostree_repo}.")
            ostree_repo.mkdir(parents=True, exist_ok=True)
            utils.run_command(
                ["ostree", "init", "--repo", ostree_repo, "--mode", "bare"])

            self.logging.info(f"Pulling {self.branch}")
            utils.run_command(
                ["ostree", "pull-local", "--repo", ostree_repo, self.repo,
                 self.branch])
            utils.run_command(
                ["ostree", "config", "--repo", ostree_repo,
                 "--group", "sysroot", "set", "bootloader", "none"])

            self.logging.info(f"Configuring {self.image} for ostree.")
            utils.run_command(
                ["ostree", "admin", "init-fs", self.rootfs])
            utils.run_command(
                ["ostree", "admin", "os-init",
                 "--sysroot", self.rootfs, "debian"])

            self.logging.info(f"Deploying {self.branch}")
            ostree_deploy = [
                "ostree", "admin", "deploy",
                "--sysroot", self.rootfs,
                "--os", "debian", self.branch]
            for arg in self.kernel_args:
                ostree_deploy.append(f"--karg={arg}")
            utils.run_command(ostree_deploy)

            self.logging.info("Setting up bootloader.")
            for d in self.rootfs.glob("ostree/deploy/debian/deploy/*.0"):
                repo_root = d
            utils.run_chroot_command(["bootctl", "install"], repo_root,
                                     efi=self.rootfs)
            shutil.copytree(self.rootfs.joinpath("boot/ostree"),
                            self.rootfs.joinpath("efi/ostree"))
            shutil.copy2(
                self.rootfs.joinpath(
                    "boot/loader/entries/ostree-1-debian.conf"),
                self.rootfs.joinpath("efi/loader/entries/ostree-0-1.conf"))
        finally:
            umount(self.rootfs)

    def post_install(self):
        pass
