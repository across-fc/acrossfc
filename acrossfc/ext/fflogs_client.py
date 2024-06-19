# stdlib
import re
import logging
from typing import List
from datetime import datetime
from urllib.parse import urlparse

# 3rd-party
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import (
    Member,
    TrackedEncounter,
    Clear,
    FFLogsFightData,
)
from acrossfc.core.constants import (
    ALL_ENCOUNTERS,
    NAME_TO_JOB_MAP,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FFLogsAPIClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

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

    def get_fc_roster(self) -> List[Member]:
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
        result = self.gql_client.execute(query, variable_values={"id": FC_CONFIG.fflogs_guild_id})
        ret = [
            Member(fcid=d["id"], name=d["name"], rank=d["guildRank"])
            for d in result["guildData"]["guild"]["members"]["data"]
            if d["guildRank"] not in FC_CONFIG.exclude_guild_ranks
        ]

        return ret

    def get_clears_for_member(
        self,
        member: Member,
        tracked_encounters: List[TrackedEncounter] = ALL_ENCOUNTERS,
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
            if "error" in boss_kill_data:
                LOG.info(f"Unable to get kill data for {member.name}: {boss_kill_data['error']}")
                continue

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

    def get_fight_data(self, fflogs_url: str) -> FFLogsFightData:
        parts = urlparse(fflogs_url)
        report_id_match = re.match(r'/reports/(.*)$', parts.path)
        if not report_id_match:
            raise ValueError(f"FFLogs URL path does not match r'/reports/(.*)$'. Received: {fflogs_url}")

        report_id = report_id_match.groups()[0]

        fight_id_match = re.match(r'fight=(\d+)', parts.fragment)
        if not fight_id_match:
            raise ValueError(f"FFLogs URL fragment does not match r'fight=(\d+)'. Received: {fflogs_url}")

        fight_id = int(fight_id_match.groups()[0])

        LOG.info(f"Getting fight data for report {report_id}, fight {fight_id}...")

        # Query header
        query_str = """
            query getReportData($report_id: String!, $fight_id: Int!) {
                reportData {
                    report(code: $report_id) {
                        fights(fightIDs: [$fight_id]) {
                            encounterID,
                            difficulty
                        }
                        playerDetails(fightIDs: [$fight_id])
                    }
                }
            }
            """
        query = gql(query_str)
        result = self.gql_client.execute(query, variable_values={"report_id": report_id, "fight_id": fight_id})
        fight_data = result["reportData"]["report"]["fights"][0]
        encounter_id = fight_data["encounterID"]
        difficulty_id = fight_data["difficulty"]
        player_details = result["reportData"]["report"]["playerDetails"]["data"]["playerDetails"]
        player_names = [player["name"] for role in player_details for player in player_details[role]]

        return FFLogsFightData(encounter_id, difficulty_id, player_names)


FFLOGS_CLIENT = FFLogsAPIClient(
    client_id=FC_CONFIG.fflogs_client_id,
    client_secret=FC_CONFIG.fflogs_client_secret,
)
