"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import logging
import shutil

from stevedore import driver

from ruck.config import Config
from ruck import exceptions


class Build(object):
    def __init__(self, state):
        self.state = state
        self.logging = logging.getLogger(__name__)
        self.config = Config(self.state)

    def build(self):
        """Build an artifact from a given configuration file."""
        self.logging.info("Running ruck.")

        self.logging.info("Loading configuration file.")
        if not self.state.config.exists():
            exceptions.ConfigError(
                f"Failed to load configuration: {self.state.config}")
        config = self.config.load_config()

        self.logging.info("Setting up workspace.")
        name = config.get("name", None)
        if name is None:
            raise exceptions.ConfigError("Manifest name is not specified.")
        self.workspace = self.state.workspace.joinpath(name)

        self.logging.info("Copying configuration to workspace.")
        shutil.copytree(
            self.state.config.parent,
            self.workspace,
            dirs_exist_ok=True)

        steps = config.get("steps")
        for step in steps:
            mgr = driver.DriverManager(
                namespace="ruck.stages",
                name=step.get("step"),
                invoke_on_load=True,
                invoke_args=(self.state,
                             step,
                             self.workspace),
                )
            mgr.driver.run()
