"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""


class RuckError(Exception):
    """Base class for microtlat exceptions."""

    def __init__(self, message=None):
        super(RuckError, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message or ""


class ConfigError(RuckError):
    """Ruck cofiguration error."""
    pass


class CommandNotFoundError(RuckError):
    """Program not found in path error."""
    pass
