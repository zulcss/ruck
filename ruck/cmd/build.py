"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import click

from ruck.build import Build
from ruck.cmd import pass_state_context
from ruck.cmd.options import config_option


@click.command(help="Build Debian artifact from manifest.")
@pass_state_context
@config_option
def build(state, config):
    Build(state).build()
