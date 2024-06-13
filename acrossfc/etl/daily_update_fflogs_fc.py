# 3rd-party
import click
import requests

# Local
from acrossfc.core.config import FC_CONFIG


@click.command()
def daily_update_fflogs_fc():
    resp = requests.get(
        f"https://www.fflogs.com/guild/update/{FC_CONFIG.fflogs_guild_id}"
    )
    if resp.status_code == 200 and "success" in resp.text:
        click.echo("Successfully updated FC roster in FFLogs.")
        return
    else:
        raise RuntimeError(f"Failed: {resp.text}")
    
