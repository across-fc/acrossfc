import os
import requests
from enum import Enum

# Local
from acrossfc.core.config import FC_CONFIG

DISCORD_API_BASE_URL = "https://discord.com/api/v10"
APP_ID = FC_CONFIG.discord_app_id
GUILD_ID = FC_CONFIG.discord_guild_id
COMMON_HEADERS = {
    "Authorization": f"Bot {FC_CONFIG.discord_bot_token}",
    "Content-Type": "application/json"
}


def _call(requests_method, path, **kwargs):
    url = os.path.join(DISCORD_API_BASE_URL, path)
    headers = COMMON_HEADERS
    resp = requests_method(url, headers=headers, **kwargs)
    if resp.status_code >= 300:
        raise Exception(f"API call failed {resp.status_code}: {resp.text}")
    return resp.json()


def _post(path, data={}):
    return _call(requests.post, path, json=data)


def _get(path, params={}):
    return _call(requests.get, path, params=params)


def _delete(path, params={}):
    return _call(requests.delete, path, params=params)


def get_user(user_id):
    return _get(f"users/{user_id}")


def get_guild_commands():
    return _get(f"applications/{APP_ID}/guilds/{GUILD_ID}/commands")


def delete_guild_command(command_id):
    return _delete(f"applications/{APP_ID}/guilds/{GUILD_ID}/commands/{command_id}")


def get_guild_member(user_id):
    return _get(f"guilds/{GUILD_ID}/members/{user_id}")


def get_guild_members():
    return _get(f"guilds/{GUILD_ID}/members?limit=500")


class InteractionResponseType(Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class Interaction:
    def __init__(self, interaction_id, interaction_token):
        self.interaaction_id = interaction_id
        self.interaction_token = interaction_token

    def _callback(
        self,
        response_type: InteractionResponseType,
        msg: str,
        ephemeral: bool = True
    ):
        _post(f"interactions/{self.interaction_id}/{self.interaction_token}/callback", {
            'type': response_type.value,
            'data': {
                'content': msg,
                'flags': (1 << 6) if ephemeral else 0
            }
        })

    def respond(self, msg: str, ephemeral: bool = True):
        self._callback(
            InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            msg,
            ephemeral=ephemeral
        )

    def thinking(self, msg: str, ephemeral: bool = True):
        self._callback(
            InteractionResponseType.DEFERRED_UPDATE_MESSAGE,
            msg,
            ephemeral=ephemeral
        )

    def followup(self, msg: str, ephemeral: bool = True):
        self._callback(
            InteractionResponseType.UPDATE_MESSAGE,
            msg,
            ephemeral=ephemeral
        )
