"""
Copyright (c) 2024 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import subprocess


def run_command(args, data=None, env=None, capture=False, shell=False,
                **kwargs):
    """Run a command in a shell."""
    try:
        if not capture:
            stdout = None
            stderr = None
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        stdin = subprocess.PIPE
        sp = subprocess.Popen(args, stdout=stdout,
                              stderr=stderr, stdin=stdin,
                              env=env, shell=shell, universal_newlines=True,
                              **kwargs)
        (out, err) = sp.communicate(data)
    except OSError:
        raise Exception(f"failed to run cmd: {args}")
    # Just ensure blank instead of none
    if not out and capture:
        out = out
    if not err and capture:
        err = err
    return (out, err)


def run_chroot_command(args, rootfs, efi=None, data=None, env=None,
                       capture=False, shell=False, **kwargs):
    """Run bubblewarap in a seperate namespace."""
    try:
        cmd = [
            "bwrap",
            "--bind", rootfs, "/",
            "--bind", f"{efi}/efi", "/efi",
            "--bind", f"{efi}/efi", "/boot/efi",
            "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
            "--proc", "/proc",
            "--dev-bind", "/dev", "/dev",
            "--bind", "/sys", "/sys",
            "--dir", "/run",
            "--bind", "/tmp", "/tmp",
            "--share-net",
            "--die-with-parent",
            "--chdir", "/",
        ]
        cmd += args
        (out, err) = run_command(cmd,
                                 data=data,
                                 env=env,
                                 capture=capture,
                                 shell=shell,
                                 **kwargs)
    except OSError:
        raise Exception(f"Failed to run chroot command: {args}")
    if not out and capture:
        out = out
    if not err and capture:
        err = err
    return (out, err)
