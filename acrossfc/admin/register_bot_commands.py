import json
import requests

# Local
from acrossfc.core.config import FC_CONFIG

# Define the command
url = f"https://discord.com/api/v10/applications/{FC_CONFIG.discord_app_id}/guilds/{FC_CONFIG.discord_guild_id}/commands"
headers = {
    "Authorization": f"Bot {FC_CONFIG.discord_bot_token}",
    "Content-Type": "application/json"
}
data = {
    "name": "list_members_with_role",
    "description": "List members with a specific role.",
    "options": [
        {
            "name": "role",
            "description": "The role to check for",
            "type": 8,  # Role type
            "required": True
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=4))
