"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import click


class State:
    def __init__(self):
        self.config = None
        self.workspace = None


# pass state between command and apt-ostree sub-commands
pass_state_context = click.make_pass_decorator(State, ensure=True)
