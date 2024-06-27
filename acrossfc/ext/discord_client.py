import os
import requests

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
    if resp.status_code > 200:
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
