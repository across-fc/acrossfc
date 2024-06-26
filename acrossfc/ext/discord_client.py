import os
import requests

# Local
from acrossfc.core.config import FC_CONFIG

DISCORD_API_BASE_URL = "https://discord.com/api/v10"
_COMMON_HEADERS = {
        "Authorization": f"Bot {FC_CONFIG.discord_bot_token}",
        "Content-Type": "application/json"
    }


def post(url, data):
    url = os.path.join(DISCORD_API_BASE_URL, url)
    headers = _COMMON_HEADERS
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code > 200:
        raise Exception(f"API call failed: {resp.text}")
    return resp.json()


def get(url, params = {}):
    url = os.path.join(DISCORD_API_BASE_URL, url)
    headers = _COMMON_HEADERS
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code > 200:
        raise Exception(f"API call failed: {resp.text}")
    return resp.json()


def delete(url, params = {}):
    url = os.path.join(DISCORD_API_BASE_URL, url)
    headers = _COMMON_HEADERS
    resp = requests.delete(url, params=params, headers=headers)
    if resp.status_code > 200:
        raise Exception(f"API call failed: {resp.text}")
    return resp.json()
