"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import logging

import click

from ruck.cmd import pass_state_context

LOG = logging.getLogger(__name__)

@click.command(
    help="Initialize ruck workspaces.")
@pass_state_context
def init(state):
    LOG.info("Initializing ruck.")

    if not state.workspace.exists():
        LOG.info(f"Creating {state.wworkspace}")
        state.workspace.mkdir(parents=True, exist_ok=True)
