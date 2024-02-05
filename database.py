# stdlib
import logging
import pickle
from typing import List, Set, Dict, Callable
from collections import defaultdict

# Local
from model import TrackedEncounter, GuildMember, Clear, ClearRate, TRACKED_ENCOUNTERS

LOG = logging.getLogger(__name__)


class Database:
    """
    This is a fake database that provides a query-like interface into in-memory state.
    """

    def __init__(self,
                 guild_members: List[GuildMember],
                 clears: List[Clear]):
        self.guild_members = guild_members
        self.clears = clears

    def save(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump([
                self.guild_members,
                self.clears
            ], f)

    @staticmethod
    def load(filename: str) -> 'Database':
        with open(filename, 'rb') as f:
            guild_members, clears = pickle.load(f)
            return Database(guild_members, clears)

    def get_clear_rates(
        self,
        guild_rank_filter: Callable[[int], bool],
        tracked_encounters: List[TrackedEncounter] = TRACKED_ENCOUNTERS
    ) -> Dict[TrackedEncounter, ClearRate]:
        eligible_members = len(list(filter(lambda member: guild_rank_filter(member.rank), self.guild_members)))

        # Single-pass through database
        cleared_members: Dict[TrackedEncounter, Set[GuildMember]] = defaultdict(set)

        for clear in self.clears:
            # Filter out non-eligible members
            if not guild_rank_filter(clear.member.rank):
                continue

            cleared_members[clear.encounter].add(clear.member)

        ret = {
            encounter: ClearRate(len(cleared_members.get(encounter, set())), eligible_members)
            for encounter in tracked_encounters
        }

        # TODO: Log report

        return ret
