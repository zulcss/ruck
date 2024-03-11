"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import subprocess


def run_command(argv, **kwargs):
    """Run a command in a shell."""
    try:
        return subprocess.run(
            argv, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e


def run_chroot(args, image, **kwargs):
    """Run a command in a seperate namespace."""
    cmd = [
        "systemd-nspawn",
        "--quiet",
        "--as-pid2",
        "-i",
        image
    ]
    cmd += args

    return run_command(cmd, **kwargs)


def bwrap(args, rootfs, workspace=None, efi=False, **kwargs):
    """Run bubblewarap in a seperate namespace."""
    cmd = [
        "bwrap",
        "--bind", rootfs, "/",
        "--proc", "/proc",
        "--dev-bind", "/dev", "/dev",
        "--bind", "/sys", "/sys",
        "--dir", "/run",
        "--bind", "/tmp", "/tmp",
        "--share-net",
        "--die-with-parent",
        "--chdir", "/",
    ]

    if efi:
        cmd += [
            "--bind", f"{workspace}/efi", "/efi",
            "--bind", "/sys/firmware/efi/efivars", "/sys/firmware/efi/efivars",
        ]

    print(cmd)
    cmd += args

    return run_command(cmd, **kwargs)
