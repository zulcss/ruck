"""
Copyright (c) 2023 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""

import logging
import sys

from rich.console import Console

from ruck.utils import run_command

# pylint: disable=wrong-import-position
import gi
gi.require_version("OSTree", "1.0")
from gi.repository import Gio, GLib, OSTree  # noqa:H301
from gi.repository.GLib import Variant, VariantDict  # noqa:H301

# Using AT_FDCWD value from fcntl.h
AT_FDCWD = -100


class Ostree:
    def __init__(self, state):
        self.logging = logging.getLogger(__name__)
        self.state = state
        self.console = Console()

    def init(self):
        """Create a new ostree repo."""
        repo = OSTree.Repo.new(Gio.File.new_for_path(
            str(self.state.repo)))
        mode = OSTree.RepoMode.ARCHIVE_Z2

        try:
            repo.create(mode)
            self.logging.info("Sucessfully initialized ostree repository.")
        except GLib.GError as e:
            self.logging.error(f"Failed to create repo: {e}")
            sys.exit(1)

    def ostree_commit(self,
                      root=None,
                      repo=None,
                      branch=None,
                      subject=None,
                      parent=None,
                      msg=None):
        """Commit rootfs to ostree repository."""
        cmd = ["ostree",
               "commit",
               "--skip-if-unchanged"
               ]
        if repo:
            cmd += [f"--repo={repo}"]
        if subject:
            cmd += [f"--subject={subject}"]
        if msg:
            cmd += [f"--body={msg}"]

        if branch:
            cmd += [f"--branch={branch}"]
        if parent:
            cmd += [f"--parent={parent}"]
        cmd += [f"--tree=dir={str(root)}"]
        return run_command(cmd)
