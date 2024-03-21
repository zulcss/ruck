"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import subprocess


def run_command(argv, **kwargs):
    """Run a command in a shell."""
    try:
        return subprocess.run(argv, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e


def run_chroot(args, image, **kwargs):
    """Run a command in a seperate namespace."""
    cmd = ["systemd-nspawn", "--quiet", "--as-pid2", "-i", image]
    cmd += args

    print(cmd)

    return run_command(cmd, **kwargs)
