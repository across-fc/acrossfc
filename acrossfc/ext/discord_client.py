import os
import time
import requests
from enum import Enum
from typing import Optional, List

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
    return resp


def _post(path, json={}):
    return _call(requests.post, path, json=json)


def _patch(path, json={}):
    return _call(requests.patch, path, json=json)


def _get(path, params={}):
    return _call(requests.get, path, params=params)


def _delete(path, params={}):
    return _call(requests.delete, path, params=params)


def get_user(user_id):
    resp = _get(f"users/{user_id}")
    return resp.json()


def get_guild_commands():
    resp = _get(f"applications/{APP_ID}/guilds/{GUILD_ID}/commands")
    return resp.json()


def delete_guild_command(command_id):
    _delete(f"applications/{APP_ID}/guilds/{GUILD_ID}/commands/{command_id}")


def get_guild_member(user_id):
    resp = _get(f"guilds/{GUILD_ID}/members/{user_id}")
    return resp.json()


def get_guild_members():
    resp = _get(f"guilds/{GUILD_ID}/members?limit=500")
    return resp.json()


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
        self.interaction_id = interaction_id
        self.interaction_token = interaction_token
        self._callback_url = f"interactions/{self.interaction_id}/{self.interaction_token}/callback"

    def respond(self, msg: str, components: Optional[List] = None, ephemeral: bool = True):
        _post(self._callback_url, {
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            'data': {
                'content': msg,
                'flags': (1 << 6) if ephemeral else 0,
                'components': components
            }
        })

    def thinking(self, ephemeral: bool = True):
        _post(self._callback_url, {
            'type': InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE.value,
            'data': {
                'flags': (1 << 6) if ephemeral else 0
            }
        })

    def update_msg(self, msg: str):
        _patch(f"webhooks/{FC_CONFIG.discord_app_id}/{self.interaction_token}/messages/@original", {
            'content': msg
        })

    def followup(self, msg: str, ephemeral: bool = True):
        _post(f"webhooks/{FC_CONFIG.discord_app_id}/{self.interaction_token}", {
            'content': msg,
            'flags': (1 << 6) if ephemeral else 0
        })

    def modal(
        self,
        custom_id: str,
        title: str,
        components: List
    ):
        _post(self._callback_url, {
            'type': InteractionResponseType.MODAL.value,
            'data': {
                'custom_id': custom_id,
                'title': title,
                'components': components
            }
        })

    def delete_original_msg(self, delay_s: Optional[int] = None):
        if delay_s is not None:
            time.sleep(delay_s)
        _delete(f"webhooks/{FC_CONFIG.discord_app_id}/{self.interaction_token}/messages/@original")
