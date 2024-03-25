"""
Copyright (c) 2023 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_log(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s %(message)s"

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.NOTSET)

    console = Console(color_system=None)

    rich_handler = RichHandler(show_path=False,
                               show_time=False,
                               show_level=False,
                               console=console)
    rich_handler.setLevel(level)
    rich_handler.setFormatter(logging.Formatter(fmt))
    rootLogger.addHandler(rich_handler)

    return rootLogger
