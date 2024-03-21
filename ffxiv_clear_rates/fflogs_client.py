# stdlib
import logging
from datetime import datetime
from typing import List, Callable

# 3rd-party
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Local
from ffxiv_clear_rates.model import (
    Member,
    TrackedEncounter,
    Clear,
    ALL_TRACKED_ENCOUNTERS,
    NAME_TO_JOB_MAP,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FFLogsAPIClient:

    def __init__(self, client_id: str, client_secret: str):
        resp = requests.post(
            "https://www.fflogs.com/oauth/token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
        )
        if resp.status_code != 200:
            raise RuntimeError(
                "Unable to get authorization token from the FFLogs API.", resp.text
            )

        access_token = resp.json()["access_token"]

        # Select your transport with a defined url endpoint
        gql_transport = AIOHTTPTransport(
            url="https://www.fflogs.com/api/v2/client",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Create a GraphQL client using the defined transport
        self.gql_client = Client(
            transport=gql_transport, fetch_schema_from_transport=True
        )

    def get_fc_roster(
        self, guild_id: int, guild_rank_filter: Callable[[int], bool]
    ) -> List[Member]:
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
        result = self.gql_client.execute(query, variable_values={"id": guild_id})
        ret = [
            Member(fcid=d["id"], name=d["name"], rank=d["guildRank"])
            for d in result["guildData"]["guild"]["members"]["data"]
            if guild_rank_filter(d["guildRank"])
        ]

        return ret

    def get_clears_for_member(
        self,
        member: Member,
        tracked_encounters: List[TrackedEncounter] = ALL_TRACKED_ENCOUNTERS,
    ) -> List[Clear]:
        LOG.info(f"Getting clear data for {member.name}...")
        # Query header
        query_str = """
            query getCharacterData($id: Int!) {
                characterData {
                    character(id: $id) {
            """

        # Add all the tracked encounters to the query
        for encounter in tracked_encounters:
            query_str += f"""
                {encounter}: encounterRankings(
                    encounterID: {encounter.encounter_id},
                    difficulty: {encounter.difficulty_id or 'null'},
                    partition: {encounter.partition_id or 'null'}
                ),
            """

        # Query footer
        query_str += """
                    }
                }
            }"""

        query = gql(query_str)
        result = self.gql_client.execute(query, variable_values={"id": member.fcid})

        clears: List[Clear] = []

        for i, boss_name in enumerate(result["characterData"]["character"]):
            # This assumes results are returned in the same order as given above
            encounter: TrackedEncounter = tracked_encounters[i]
            boss_kill_data = result["characterData"]["character"][boss_name]
            if boss_kill_data["totalKills"] == 0:
                continue

            for kill in result["characterData"]["character"][boss_name]["ranks"]:
                clears.append(
                    Clear(
                        member=member.fcid,
                        encounter=encounter,
                        start_time=datetime.fromtimestamp(
                            # Python takes in seconds, API returns milliseconds
                            kill["startTime"]
                            / 1000
                        ),
                        historical_pct=kill["historicalPercent"],
                        report_code=kill["report"]["code"],
                        report_fight_id=kill["report"]["fightID"],
                        job=NAME_TO_JOB_MAP[kill["spec"]],
                        locked_in=kill["lockedIn"] == "true",
                    )
                )

        return clears
