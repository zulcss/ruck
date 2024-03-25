"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import os

from omegaconf import OmegaConf
import yaml

from ruck import exceptions

def get_config(config, subkey):
    return OmegaConf.select(
        config, subkey, throw_on_missing=False)

def include_constructor(loader, node):
    filename = node.value
    if not os.path.isfile(filename) or filename.split(".")[-1] != "yaml":
        # (FIXME) chuck - better error message here
        raise exceptions.ConfigError("Not valid yaml.")

    with open(filename, "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


yaml.add_constructor("!include", include_constructor, Loader=yaml.SafeLoader)


class Config(object):
    """load the configuration file from the CLI."""
    def __init__(self, state):
        self.state = state

    def load_config(self):
        """Load the manifest.yaml"""
        try:
            with open(self.state.config, "r") as f:
                try:
                    return OmegaConf.create(yaml.safe_load(f))
                except yaml.YAMLError as error:
                    raise exceptions.ConfigError(
                        f"{self.state.config} failed validateion: {error}.")
        except OSError as e:
            raise exceptions.ConfigError(
            f"Configuration not found: {self.sstate.config}")
