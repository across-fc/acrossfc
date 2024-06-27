# 3rd-party
import click

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext import discord_client as DISCORD_API


@click.group()
def axd():
    pass


@axd.command()
def register_guild_commands():
    # /fc_points
    DISCORD_API._post(
        f"applications/{FC_CONFIG.discord_app_id}/guilds/{FC_CONFIG.discord_guild_id}/commands",
        {
            "name": "fc_points",
            "description": "Make a submission or check FC points"
        }
    )

    # FC Points button
    DISCORD_API._post(
        f"channels/{FC_CONFIG.discord_fc_action_channel_id}/messages",
        {
            "content": "Points for the current tier are now closed. The next tier will begin on <t:1719565200:f>.",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "FC Points",
                            "style": 1,
                            "custom_id": "fc_points_button",
                            "disabled": True
                        }
                    ]
                }
            ]
        }
    )
