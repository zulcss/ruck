"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging
import os
import shutil

from ruck import exceptions
from ruck.schema import validate
from ruck.stages.base import Base
from ruck.utils import run_command

SCHEMA = {
    "image": {"type": "string", "required": True},
    "options": {
        "type": "dict",
        "schema": {
            "definition": {"type": "string", "required": True},
            "size": {"type": "string", "required": True},
        }
        },
    }


class DiskPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")

        self.repart = shutil.which("systemd-repart")

    def run(self):
        """Create a DDI based disk image using systemd-repart."""
        self.logging.info("Creating DDI disk.")
        if self.repart is None:
            raise exceptions.CommandNotFoundError(
                "systemd-repart is not found.")

        state = validate(self.config, SCHEMA)
        if not state:
            raise exceptions.ConfigError("Configuration is invalid.")

        image = self.workspace.joinpath(self.config.get("image"))
        if image.exists():
            # systemd-repart errors out if image already exists.
            self.logging.info(f"Removing {image}.")
            os.unlink(image)
        definitions = self.workspace.joinpath(self.options.get("definition"))
        if not definitions.exists():
            raise exceptions.ConfigError(f"Unable to find {definitions}.")
        size = self.options.get("size")

        run_command([
            self.repart,
            "--definitions", str(definitions),
            "--empty=create",
            "--size", size,
            "--dry-run=no",
            "--discard=no",
            "--offline=true",
            "--no-pager",
            str(image)],
            cwd=self.workspace)
