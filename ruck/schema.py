"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

from cerberus import Validator

from ruck.exceptions import SchemaError


def validate(action, schema):
    """Validates the action block based on the cerberus schema."""

    v = Validator(schema)
    status = v.validate(action)

    if not status:
        raise SchemaError("Invalid syntax: {0}".format(v.errors))
    else:
        return status
