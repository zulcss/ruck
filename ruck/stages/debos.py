"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import shutil

from ruck.stages.base import Base
from ruck.utils import run_command


class DebosPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        self.logging = logging.getLogger(__name__)

        self.options = self.config.get("options")

    def run(self):
        self.logging.info("Running debos.")

        recipe = self.options.get("recipe")
        repo = self.options.get("repo")
        branch = self.options.get("branch")

        ostree_repo = self.workspace.joinpath("ostree_repo")
        if ostree_repo.exists():
            shutil.rmtree(ostree_repo)

        run_command(["ostree", "init", "--repo", ostree_repo])
        run_command(["ostree", "pull-local", "--repo", ostree_repo, repo, branch])
        run_command(
            ["debos", "-t", f"branch:{branch}", "-v", recipe], cwd=self.workspace
        )
