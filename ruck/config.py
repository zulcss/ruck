"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import os

import yaml

from ruck import exceptions


def include_constructor(loader, node):
    filename = node.value
    print(filename)
    if not os.path.isfile(filename) or filename.split(".")[-1] != "yaml":
        # (FIXME) chuck - better error message here
        raise exceptions.ConfigError("Not valid yaml.")

    with open(filename, "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


yaml.add_constructor("!include", include_constructor, Loader=yaml.SafeLoader)


class Config(object):
    def __init__(self, state):
        self.state = state

    def load_config(self):
        """Load the manifest.yaml"""
        with open(self.state.config, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                raise exceptions.ConfigError("Unable to parse configuration file.")
