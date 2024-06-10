import click
import logging

# Local
from acrossfc import root_logger


@click.group()
@click.option('-t', '--test', is_flag=True, show_default=True, default=False,
              help="Run in test mode")
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False,
              help="Turn on verbose logging")
@click.option('-c', '--fc-config',
              help="Path to the FC config file")
def axr(test, verbose, fc_config):
    if verbose:
        root_logger.setLevel(logging.DEBUG)
    # TODO: If test mode... do stuff
    # TODO: If FC config... do stuff


@axr.command()
def update_fflogs():
    click.echo("update_fflogs")


@axr.command()
def extract_fflogs_data():
    # TODO: Download FFLogs data
    # TODO: Save local file
    # TODO: Save to S3 if necessary
    click.echo("Extract FFLogs data")


@axr.command()
def fc_roster():
    click.echo("fc_roster")


@axr.command()
def clear_rates():
    click.echo("clear_rates")


@axr.command()
def clear_chart():
    click.echo("clear_chart")


@axr.command()
def clear_order():
    click.echo("clear_order")


@axr.command()
def cleared_roles():
    click.echo("cleared_roles")


@axr.command()
def cleared_jobs_by_member():
    click.echo("cleared_jobs_by_member")

@axr.command()
def who_cleared_recently():
    click.echo("who_cleared_recently")


@axr.command()
def ppl_with_clear():
    click.echo("ppl_with_clear")


@axr.command()
def ppl_without_clear():
    click.echo("ppl_without_clear")
