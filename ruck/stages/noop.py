"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
from ruck.stages.base import Base


class NoopPlugin(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace

    def run(self):
        print(self.config)
