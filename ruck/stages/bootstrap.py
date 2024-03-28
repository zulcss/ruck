"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import os
import shutil

from ruck.config import get_config
from ruck import exceptions
from ruck.stages.base import Base
from ruck import utils


class BootstrapPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

    def preflight_check(self):
        self.logging.info("Performing pre-flight checks.")
        self.mmdebstrap = shutil.which("mmdebstrap")
        if not self.mmdebstrap:
            raise exceptions.CommandNotFoundError(
                "mmdebstroap is not found.")
        if not self.config.options.suite:
            raise exceptions.ConfigError(
                "Suite is not specified.")
        if not self.config.options.target:
            raise exceptions.ConfigError(
                "target is not specified.")
        self.logging.info(self.config.options.target)

    def run(self):
        """Run the mmdebstrap command."""
        self.logging.info(f"Running mmdebstrap.")

        cmd = [
            self.mmdebstrap,
            "--architecture", self.config.options.architecture,
            "--verbose",
        ]

        # Extend mmdesbtrap configuration, see manpage for details.
        packages = get_config(self.config, "options.packages")
        if packages:
            cmd.extend([f"--include={', '.join(packages)}"])

        repo = get_config(self.config, "options.repo")
        if repo:
            if not os.path.isfile(repo) and not os.path.exists():
                raise exceptions.ConfigError(
                    "Repo configuration is not a file")
            repo = self.workspace.joinpath(repo)
        customize_hooks = get_config(self.config, "options.customize_hooks")
        if customize_hooks:
            cmd.extend([f"--customize-hook={hook}"
                        for hook in customize_hooks])
        components = get_config(self.config, "options.compoents")
        if components:
            cmd.extend([f"--components={','.join(components)}"])
        variant = get_config(self.config, "options.varant")
        if variant:
            cmd.extend([f"--variant={variant}"])
        hooks = get_config(self.config, "options.hooks")
        if hooks:
            cmd.extend([f"--hook-directory={hook}" for hook in hooks])
        setup_hooks = get_config(self.config, "options.setup_hooks")
        if setup_hooks:
            cmd.extend([f"--setup-hook={hook}" for hook in setup_hooks])
        extract_hooks = get_config(self.config, "options.extract_hooks")
        if extract_hooks:
            cmd.extend([f"--extract-hook={hook}"
                        for hook in extract_hooks])
        essential_hooks = get_config(self.config, "options.essential_hooks")
        if essential_hooks:
            cmd.extend([f"--essential-hook={hook}"
                        for hook in essential_hooks])
        apt_hooks = get_config(self.config, "options.apt_hooks")
        if apt_hooks:
            cmd.extend([f"--aptopt={hook}" for hook in apt_hooks])
        mode = get_config(self.config, "options.mode")
        if mode:
            cmd.extend([f"--mode={mode}"])
        keyring = get_config(self.config, "options.keyring")
        if keyring:
            cmd.extend([f"--keyring={hook}" for hook in keyring])
        dpkg_opts = get_config(self.config, "options.dpkgopt")
        if dpkg_opts:
            cmd.extend([f"--dpkgopts='{hook}'" for hook in dpkg_opts])

        suite = get_config(self.config, "options.suite")
        target = self.workspace.joinpath(
            get_config(self.config, "options.target"))
        cmd.extend([suite, target])
        if repo is not None:
            # include our mirror from the manifest.
            cmd.extend([repo])
        utils.run_command(cmd)

    def post_install(self):
        pass
