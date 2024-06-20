# 3rd-party
import click
import logging

# Local
from acrossfc import root_logger
from .submissions import submit_fc_pf


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
def axs(verbose):
    if verbose:
        root_logger.setLevel(logging.DEBUG)


cmd = submit_fc_pf
cmd = click.option('-u', '--fflogs-url')(cmd)
cmd = click.option('-i', '--fc-pf-id', required=True)(cmd)
axs.command(
    name='submit-fc-pf',
    help='Make a submission for an FC PF event'
)(cmd)
