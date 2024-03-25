"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging
import os
import shutil

from ruck import exceptions
from ruck.stages.base import Base
from ruck.utils import run_command


class RepartPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.repart = shutil.which("systemd-repart")

    def preflight_check(self):
        """Check for valid options."""
        if self.repart is None:
            raise exceptions.CommandNotFoundError(
                "systemd-repart is not found.")
        if self.config.options.image is None:
            raise exceptions.ConfigError(
                "Image to create is not specified.")
        if self.config.options.size is None:
            raise exceptions.ConfigError(
                "Image size is not specified.")
        self.image = self.workspace.joinpath(
                        self.config.options.image)
        if self.image.exists():
            # systemd-repart errors out if image already exists.
            self.logging.info(f"Removing {self.image}")
        self.definitions = self.workspace.joinpath(
                self.config.options.definitions)
        if not self.definitions.exists():
            raise exceptions.ConfigError(
                f"{self.definitions} does not exist.")

    def run(self):
        """Create a DDI based disk image using systemd-repart."""
        self.logging.info("Creating disk via systemd-repart.")

        run_command([
            self.repart,
            "--definitions", str(self.definitions),
            "--empty=create",
            "--size", self.config.options.size,
            "--dry-run=no",
            "--discard=no",
            "--no-pager",
            str(self.image)],
            cwd=self.workspace)

    def post_install(self):
        self.logging.info(f"{self.image} can be found at {self.workspace}.")
