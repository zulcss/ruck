"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import yaml

from ruck import exceptions


class Config(object):
    def __init__(self, state):
        self.state = state

    def load_config(self):
        """Load the manifest.yaml"""
        with open(self.state.config, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                raise exceptions.ConfigError(
                    "Unable to parse configuration file.")
