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


def run_chroot(args, rootfs, **kwargs):
    """Run a command in a seperate namespace."""
    cmd = [
        "bwrap",
        "--proc", "/proc",
        "--dev", "/dev",
        "--dir", "/run",
        "--bind", "/tmp", "/tmp",
        "--bind", f"{rootfs}/boot", "/boot",
        "--bind", f"{rootfs}/efi", "/efi",
        "--bind", f"{rootfs}/usr", "/usr",
        "--bind", f"{rootfs}/etc", "/etc",
        "--bind", f"{rootfs}/var", "/var",
        "--symlink", "/usr/lib", "/lib",
        "--symlink", "/usr/lib64", "/lib64",
        "--symlink", "/usr/bin", "/bin",
        "--symlink", "/usr/sbin", "/sbin",
        "--share-net",
        "--die-with-parent",
        "--chdir", "/",
    ]
    cmd += args

    return run_command(cmd, **kwargs)
