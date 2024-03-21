"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import pathlib

from ruck import exceptions, utils
from ruck.stages.base import Base


class OstreeBase(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace

        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")


class OstreeInitPlugin(OstreeBase):
    def run(self):
        self.logging.info("Creating ostree repository.")

        repo = pathlib.Path(self.options.get("repo"))
        mode = self.options.get("mode")

        if repo.exists():
            raise exceptions.ConfigError(f"{repo} already exists.")

        utils.run_command(["ostree", "init", "--repo", repo, "--mode", mode])
