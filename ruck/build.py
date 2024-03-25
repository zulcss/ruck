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

        self.arch = ["amd64", "arm64"]

    def build(self):
        """Build an artifact from a given configuration file."""
        self.logging.info("Running ruck.")

        self.logging.info(
           f"Loading configuration file: {self.state.config}")
        if not self.state.config.exists():
            exceptions.ConfigError(
                f"Failed to load configuration: {self.state.config}")
        config = self.config.load_config()

        if config.name is None:
            raise exceptions.ConfigError("Manifest name is not specified.")
        if config.architecture is None:
            raise exceptions.ConfigError(
                "Manifest archtitecture is not specified.")
        if config.architecture not in self.arch:
            raise exceptions.ConfigError(
                f"{config.architecture} is not supported.")
        
        if config.version is None:
            raise exceptions.ConfigError("Version si not specified..")
        if config.schemaVersion is None:
            raise exceptions.ConfigError("Schema version is not specified.")
        if config.schemaVersion != 1:
            raise exceptions.ConfigError(
                f"{config.schemaVersion} is not supported.")

        self.workspace = self.state.workspace.joinpath(config.name)
        self.logging.info(f"Setting up workspace: {self.workspace}")
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.logging.info("Copying configuration to workspace.")
        shutil.copytree(
            self.state.config.parent,
            self.workspace,
            dirs_exist_ok=True)
    
        if config.phases:
            self.logging.info("Running phases...")
            for p in config.phases:
                self.logging.info(p.name)

                self.logging.info(f"Loading {p.stage} step.")
                mgr = driver.DriverManager(
                        namespace="ruck.stages",
                        name=p.stage,
                        invoke_on_load=True,
                        invoke_args=(self.state, p,
                                     self.workspace)
                      )

                self.logging.info("Running preflight check.")
                mgr.driver.preflight_check()

                self.logging.info("Running step.")
                mgr.driver.run()

                self.logging.info("Running post install.")
                mgr.driver.post_install()

        else:
            raise exception.ConfigException(
                "No phases found please check the manifest.")
