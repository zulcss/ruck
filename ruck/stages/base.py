"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from abc import ABC, abstractmethod


class Base(ABC):
    def __init__(self):
        self.workspace = None
        self.rootfs = None

    @abstractmethod
    def run(self):
        pass
