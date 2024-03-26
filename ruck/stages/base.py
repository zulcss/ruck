"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from abc import ABC
from abc import abstractmethod
import logging


class Base(ABC):
    def __init__(self):
        self.workspace = None
        self.rootfs = None

    @abstractmethod
    def preflight_check(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def post_install(self):
        pass

class OstreeBase(Base):
    def __init__(self, state, config, workspace):
        self.state = state
        self.config = config
        self.workspace = workspace
        
        self.logging = logging.getLogger(__name__)
