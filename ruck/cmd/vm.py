"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import click

from ruck.cmd.options import disk_option
from ruck.cmd.options import name_option
from ruck.cmd import pass_state_context
from ruck.vm import VM


@click.group(
    help="Perform operations on ruck virtual machines.")
@pass_state_context
def vm(state):
    pass


@click.command(
    help="show all virtual machines."
)
@pass_state_context
def show(state):
    VM(state).list()


@click.command(
    help="Create a virtual machine."
)
@pass_state_context
@name_option
@disk_option
def create(state, name, disk):
    VM(state).create()


@click.command(
    help="Shutdown and remove virtual macine."
)
@pass_state_context
@name_option
def shutdown(state, name):
    VM(state).shutdown()


vm.add_command(show)
vm.add_command(create)
vm.add_command(shutdown)
