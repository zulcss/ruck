"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import click

from ruck.cmd.build import build
from ruck.cmd.init import init
from ruck.cmd.options import workspace_option
from ruck.cmd import pass_state_context
from ruck.log import setup_log


@click.group(
    help="Debian build system."
)
@pass_state_context
@workspace_option
def cli(state, workspace):
    setup_log()


def main():
    cli(prog_name="ruck")


# ruck sub-commands
cli.add_command(build)
cli.add_command(init)
