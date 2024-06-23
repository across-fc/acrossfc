# 3rd-party
import click
import logging

# Local
from acrossfc import root_logger
from .submissions import submit_fflogs


@click.group()
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
def axs(verbose):
    if verbose:
        root_logger.setLevel(logging.DEBUG)


cmd = submit_fflogs
cmd = click.option('-l', '--fflogs-url', required=True)(cmd)
cmd = click.option('-u', '--submitted-by-name', required=True)(cmd)
cmd = click.option('-c', '--submission-channel', required=True)(cmd)
cmd = click.option('--is-static', is_flag=True, default=False)(cmd)
cmd = click.option('--is-fc-pf', is_flag=True, default=False)(cmd)
cmd = click.option('-i', '--fc-pf-id')(cmd)
axs.command(
    name='submit-fflogs',
    help='Make a submission with FFLogs'
)(cmd)
