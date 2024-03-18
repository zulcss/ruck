"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""
import pathlib

import click

from ruck.cmd import State


def config_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.config = pathlib.Path(value)

        return value
    return click.option(
        "-C", "--config",
        help="Path to configuration file.",
        nargs=1,
        callback=callback
    )(f)


def workspace_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.workspace = pathlib.Path(value)
        return value
    return click.option(
        "--workspace",
        help="Path to the ruck workspace.",
        nargs=1,
        default="/var/tmp/ruck",
        required=True,
        callback=callback
    )(f)


""" Virtual machine options. """


def name_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.name = value
        return value
    return click.option(
        "--name",
        help="Name of virtual machine",
        nargs=1,
        required=True,
        callback=callback
    )(f)


def disk_option(f):
    def callback(ctxt, param, value):
        state = ctxt.ensure_object(State)
        state.disk = value
        return value
    return click.option(
        "--disk",
        help="Path to the virtual machine's disk",
        nargs=1,
        required=True,
        callback=callback
    )(f)
