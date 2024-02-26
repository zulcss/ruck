import click

from ruck.cmd import pass_state_context
from ruck.cmd.options import config_option
from ruck.build import Build

@click.command(
    help="Build Debian artifact from manifest.")
@pass_state_context
@config_option
def build(state, config):
    Build(state).build()
