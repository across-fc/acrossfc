import click


@click.group()
def axs():
    pass


@axs.command()
def submit_fc_pf():
    click.echo("Submit: FC PF")


@axs.command()
def submit_admin():
    # TODO: Crafting / Gathering team (50)
    # TODO: Be a mentor (25)
    # TODO: Static - any (20)
    click.echo("Submit: Admin")


@axs.command()
def submit():
    # TODO: Mentor tickets?? Can I detect the channel? (10)
    click.echo("Submit: Normal")
