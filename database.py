# stdlib
import logging
import pickle
from datetime import date
from typing import List, Set, Tuple, Dict, Callable, Optional
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
                 clears: List[Clear],
                 guild_rank_filter: Optional[Callable[[int], bool]] = None):
        # Filter data by guild_rank
        if guild_rank_filter is not None:
            self.guild_members = [
                member
                for member in guild_members
                if guild_rank_filter(member.rank)
            ]
            self.clears = [
                clear
                for clear in clears
                if guild_rank_filter(clear.member.rank)
            ]
        else:
            self.guild_members = guild_members
            self.clears = clears

        self.cleared_members_by_encounter: Dict[TrackedEncounter, Set[GuildMember]] = defaultdict(set)
        for clear in self.clears:
            self.cleared_members_by_encounter[clear.encounter].add(clear.member)

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
        tracked_encounters: List[TrackedEncounter] = TRACKED_ENCOUNTERS
    ) -> Dict[TrackedEncounter, ClearRate]:
        ret = {
            encounter: ClearRate(
                len(self.cleared_members_by_encounter.get(encounter, set())),
                len(self.guild_members)
            )
            for encounter in tracked_encounters
        }

        # TODO: Log report

        return ret

    def get_uncleared_members_by_encounter(
        self,
        encounter: TrackedEncounter
    ) -> Set[GuildMember]:
        ret = [
            member
            for member in self.guild_members
            if member not in self.cleared_members_by_encounter[encounter]
        ]

        return ret

    def get_clear_chart(self) -> Dict[TrackedEncounter, List[Tuple[date, Set[GuildMember]]]]:
        # {
        #     <encounter>: [
        #         (<date>, <cleared_members_set>),
        #         (<date>, <cleared_members_set>),
        #         (<date>, <cleared_members_set>),
        #         ...
        #     ]
        # }
        encounter_cumulative_clears_by_date: Dict[
            TrackedEncounter,
            List[Tuple[date, Set[GuildMember]]]
        ] = defaultdict(list)

        for clear in sorted(self.clears, key=lambda clear: clear.start_time):
            clear_date = clear.start_time.date()
            if len(encounter_cumulative_clears_by_date[clear.encounter]) == 0:
                encounter_cumulative_clears_by_date[clear.encounter].append(
                    (
                        clear_date,
                        {clear.member}
                    )
                )
                continue

            current_cleared_members = encounter_cumulative_clears_by_date[clear.encounter][-1][1]
            if clear.member not in current_cleared_members:
                new_datapoint = (
                    clear_date,
                    current_cleared_members | {clear.member}
                )
                if clear_date > encounter_cumulative_clears_by_date[clear.encounter][-1][0]:
                    encounter_cumulative_clears_by_date[clear.encounter].append(new_datapoint)
                else:
                    encounter_cumulative_clears_by_date[clear.encounter][-1] = new_datapoint

        return encounter_cumulative_clears_by_date
