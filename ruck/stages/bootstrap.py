"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import shutil

from ruck import exceptions
from ruck.schema import validate
from ruck.stages.base import Base
from ruck import utils

SCHEMA = {
    "target": {"type": "string"},
    "options": {
        "type": "dict",
        "schema": {
                "target": {"type": "string", "required": True},
                "suite": {"type": "string", "required": True},
                "packages": {"type": "list"},
                "variant": {"type": "string"},
                "components": {"type": "list"},
                "hooks": {"type": "list"},
                "setup-hooks": {"type": "list"},
                "extract-hooks": {"type": "list"},
                "customize-hooks": {"type": "list"},
                "essential-hooks": {"type": "list"},
            },
        }
}


class BootstrapPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")

        self.mmdebstrap = shutil.which("mmdebstrap")

    def run(self):
        """Run the mmdebstrap command."""
        self.logging.info("Running mmdebstrap.")
        if self.mmdebstrap is None:
            raise exceptions.CommandNotFoundError("mmdebstrap is not found.")

        status = validate(self.config, SCHEMA)
        if not status:
            raise exceptions.ConfigError("Invalid schema.")

        suite = self.options.get("suite")
        target = self.config.get("target")

        cmd = [
            self.mmdebstrap,
            "--architecture", "amd64",
            "--verbose",
        ]

        # Install extra packages.
        packages = self.options.get("packages", None)
        if packages:
            cmd.extend([f"--include={','.join(packages)}"])

        customize_hooks = self.options.get("customize-hooks", None)
        if customize_hooks:
            cmd.extend([f"--customize-hook={hook}"
                        for hook in customize_hooks])

        # Enable extra components (main, non-free, etc).
        components = self.options.get("components", None)
        if components:
            cmd.extend([f"--components={','.join(components)}"])
        cmd.extend([suite, target])
        utils.run_command(cmd, cwd=self.workspace)

        # Enable variants.
        variant = self.options.get("variant", None)
        if variant:
            cmd.extend([f"--variant={variant}"])

        # Enable hooks.
        hooks = self.options.get("hooks", None)
        if hooks:
            cmd.extend([f"--hook-directory={hook}" for hook in hooks])

        # Enable setup hooks
        setup_hooks = self.options.get("setup-hooks", None)
        if setup_hooks:
            cmd.extend([f"--setup-hook={hook}" for hook in setup_hooks])

        # Enable extract hooks.
        extract_hooks = self.options.get("extract-hook", None)
        if extract_hooks:
            cmd.extend(
                [f"--extract-hook={hook}" for hook in extract_hooks])

        # Enable customization hooks.
        customize_hooks = self.options.get("customize-hooks", None)
        if customize_hooks:
            cmd.extend([f"--customize-hook={hook}"
                        for hook in customize_hooks])
        # Enable essential hooks.
        essential_hooks = self.options.get("essential-hooks", None)
        if essential_hooks:
            cmd.extend([f"--essential-hook={hook}"
                       for hook in essential_hooks])

        cmd.extend([suite, target])
        utils.run_command(cmd, cwd=self.workspace)
