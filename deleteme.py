import click


@click.group()
def g():
    print("Running group")


@g.command()
def c():
    print("Running command")


command = g.get_command(None, 'c')
click.Context(c).invoke(g)
