import click

from ruck.cmd import pass_state_context

@click.command
@pass_state_context
def cli(state):
    pass

def main():
    cli(prog_name="ruck")
