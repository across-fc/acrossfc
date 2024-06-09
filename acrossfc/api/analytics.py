import click


@click.group()
def axr():
    pass


@axr.command()
def update_fflogs():
    click.echo("update_fflogs")


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
