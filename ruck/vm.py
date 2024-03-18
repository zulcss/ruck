"""
Copyright (c) 2023 Wind River Systems, Inc.

SPDX-License-Identifier: Apache-2.0

"""
import logging
import sys

import libvirt
from rich import console
from rich.table import Table

from ruck.utils import run_command


class VM(object):
    def __init__(self, state):
        self.state = state
        self.logging = logging.getLogger(__name__)
        self.console = console.Console()

    def list(self):
        """List all current domains."""
        conn = self._connect()

        domains = [domain for domain in conn.listAllDomains(0)]
        if len(domains) == 0:
            self.console.print("No vms are running.")
            sys.exit(1)

        table = Table()

        table.add_column("ID")
        table.add_column("Name")
        table.add_column("State")

        for domain in domains:
            table.add_row(str(domain.ID()),
                          domain.name(),
                          self._get_state(domain.info()[0]))

        self.console.print(table)

        conn.close()

    def create(self):
        """Create libvirt vm but dont start it."""
        self.logging.info(f"Staring {self.state.name}")

        run_command(
            ["virt-install",
             "--connect", "qemu:///system",
             "--boot", "loader=/usr/share/ovmf/OVMF.fd",
             "--machine", "q35",
             "--name", self.state.name,
             "--ram", "8096",
             "--vcpus", "4",
             "--os-variant", "debiantesting",
             "--disk", f"path={self.state.disk}",
             "--noautoconsole",
             "--check", "path_in_use=off",
             "--import"])

    def shutdown(self):
        """Remove virtual machine from disk."""
        self.logging.info(f"Destroying {self.state.name}")
        run_command(
            ["virsh", "destroy", self.state.name])
        self.logging.info(f"Removing {self.state.name}.")
        run_command(
            ["virsh", "undefine", self.state.name])

    def _connect(self):
        """Connect to the libvirt daemon."""
        try:
            return libvirt.openReadOnly(None)
        except libvirt.libvirtError as e:
            self.logging.errror(
                "Unale to connect to livbirt: `%s'" %
                e.message.replace("\r", ""))

    def _get_state(self, state):
        """Lookup libvirt states."""
        libvirt_states = {
            libvirt.VIR_DOMAIN_RUNNING: "Running",
            libvirt.VIR_DOMAIN_SHUTOFF: "Shutoff",
            libvirt.VIR_DOMAIN_SHUTDOWN: "Shutdown",
            libvirt.VIR_DOMAIN_PAUSED: "Paused",
            libvirt.VIR_DOMAIN_NOSTATE: "Nostate",
            libvirt.VIR_DOMAIN_BLOCKED: "Blocked",
            libvirt.VIR_DOMAIN_CRASHED: "Crashed",

        }
        return libvirt_states.get(state)
