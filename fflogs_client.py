# stdlib
import logging
from typing import Dict, List, Callable

# 3rd-party
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Local
from model import GuildMember, TrackedEncounter, ClearRate, TRACKED_ENCOUNTERS

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FFLogsAPIClient:

    def __init__(self, client_id: str, client_secret: str):
        resp = requests.post(
            'https://www.fflogs.com/oauth/token',
            auth=(client_id, client_secret),
            data={
                'grant_type': 'client_credentials'
            })
        if resp.status_code != 200:
            raise RuntimeError('Unable to get authorization token from the FFLogs API.', resp.text)

        access_token = resp.json()['access_token']

        # Select your transport with a defined url endpoint
        gql_transport = AIOHTTPTransport(url="https://www.fflogs.com/api/v2/client",
                                         headers={'Authorization': f'Bearer {access_token}'})

        # Create a GraphQL client using the defined transport
        self.gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)

    def get_fc_roster(self, guild_id: int) -> List[GuildMember]:
        query = gql(
            """
            query getGuildData($id: Int!) {
                guildData {
                    guild(id: $id) {
                        members {
                            data {
                                id,
                                name,
                                guildRank
                            }
                        }
                    }
                }
            }
            """
        )
        result = self.gql_client.execute(query, variable_values={'id': guild_id})
        ret = [
            GuildMember(d['id'], d['name'], d['guildRank'])
            for d in result['guildData']['guild']['members']['data']
        ]

        # TODO: Log report

        return ret

    def get_cleared_fights_for_user(
        self,
        user_id: int,
        tracked_encounters: List[TrackedEncounter]
    ) -> List[TrackedEncounter]:
        # Query header
        query_str = """
            query getCharacterData($id: Int!) {
                characterData {
                    character(id: $id) {
            """ 

        # Add all the tracked encounters to the query
        for encounter in tracked_encounters:
            query_str += f"""
                {encounter.boss.name}: encounterRankings(
                    encounterID: {encounter.boss.value},
                    difficulty: {encounter.difficulty.value if encounter.difficulty is not None else 'null'}
                ),
            """

        # Query footer
        query_str += """
                    }
                }
            }"""

        query = gql(query_str)
        result = self.gql_client.execute(query, variable_values={'id': user_id})
        ret = [
            encounter
            for encounter in tracked_encounters
            if result['characterData']['character'][encounter.boss.name]['totalKills'] > 0
        ]

        # TODO: Log report

        return ret

    def get_clear_rates(
        self,
        guild_id: int,
        guild_rank_filter: Callable[[int], bool],
        tracked_encounters: List[TrackedEncounter] = TRACKED_ENCOUNTERS
    ) -> Dict[TrackedEncounter, ClearRate]:
        LOG.info(f'Getting clear rates for guild {guild_id}...')

        clears: Dict[TrackedEncounter, int] = {
            encounter: 0
            for encounter in tracked_encounters
        }

        fc_roster: List[GuildMember] = self.get_fc_roster(guild_id)
        eligible_members = 0

        for member in fc_roster:
            if guild_rank_filter(member.rank):
                LOG.debug(f'Getting cleared encounters for {member.name}...')
                eligible_members += 1
                cleared_encounters: List[TrackedEncounter] = self.get_cleared_fights_for_user(
                    member.id,
                    tracked_encounters=tracked_encounters
                )
                for encounter in cleared_encounters:
                    clears[encounter] += 1

        ret = {
            encounter: ClearRate(clears.get(encounter, 0), eligible_members)
            for encounter in tracked_encounters
        }

        # TODO: Log report

        return ret
