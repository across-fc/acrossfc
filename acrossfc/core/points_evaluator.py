# stdlib
import uuid
import time
import logging
from typing import Optional, List
from datetime import timedelta

# Local
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import (
    PointsEvent,
    Member,
    FFLogsFightData,
    PointsCategory,
    Clear
)
from acrossfc.core.constants import (
    CURRENT_EXTREMES,
    CURRENT_UNREAL,
    CURRENT_SAVAGES,
    CURRENT_SAVAGE_TO_POINTS_CATEGORY,
    CURRENT_CRITERIONS,
    ULTIMATES
)
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT
from acrossfc.ext.ddb_client import DDB_CLIENT

LOG = logging.getLogger(__name__)


class PointsEvaluator:
    def __init__(
        self,
        fflogs_url: str,
        is_fc_pf: bool,
        is_static: bool,
        fc_pf_id: Optional[str]
    ):
        self.fight_data: FFLogsFightData = FFLOGS_CLIENT.get_fight_data(fflogs_url)
        self.fc_roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
        self.is_fc_pf = is_fc_pf
        self.is_static = is_static
        self.fc_pf_id = fc_pf_id
        self.fc_members_in_fight: List[Member] = []
        self.points_events = []
        self.notes = []

        self.load_fc_member_ids()
        self.eval_fc_pf()
        self.eval_fc_high_end_content()
        self.eval_vet_and_first_clears()

    def load_fc_member_ids(self):
        player_names_set = set(self.fight_data.player_names)
        for member in self.fc_roster:
            if member.name in player_names_set:
                self.fc_members_in_fight.append(member)
                player_names_set.remove(member.name)

        if len(player_names_set) > 0:
            LOG.debug(f"Skipping points registration for {player_names_set}: Not in FC roster")

    def eval_fc_pf(self):
        """
        Participate in ANY FC PF listing (10)
        """
        if self.is_fc_pf:
            for member in self.fc_members_in_fight:
                category = PointsCategory.FC_PF
                self.points_events.append(
                    PointsEvent(
                        uuid=str(uuid.uuid4()),
                        member_id=member.fcid,
                        points=category.points,
                        category=category,
                        description=f"FC PF: {self.fc_pf_id or 'Unknown'}",
                        ts=int(time.time()),
                    )
                )
        else:
            self.notes.append("Not an FC PF ticket. No FC PF event participation points awarded.")

    def eval_fc_high_end_content(self):
        """
        Participate in a Savage/Unreal/Extreme/Ultimate/Criterion
        Full or partial FC party (full-lockout or clear)
        STATICS DO NOT COUNT (10)
        """
        if self.is_static:
            self.notes.append("Statics do not qualify for FC high-end content points")
            return

        full_or_partial_fc = (len(self.fc_members_in_fight) >= 4)

        # TODO: How to scan for statics? By frequency?

        e = self.fight_data.encounter
        if e in CURRENT_EXTREMES:
            category = PointsCategory.FC_EXTREME
            description = f"FC Extreme: {e.name}"
        elif e == CURRENT_UNREAL:
            category = PointsCategory.FC_UNREAL
            description = f"FC Unreal: {e.name}"
        elif e in CURRENT_SAVAGES:
            category = PointsCategory.FC_SAVAGE
            description = f"FC Savage: {e.name}"
        elif e in CURRENT_CRITERIONS:
            category = PointsCategory.FC_CRITERION
            description = f"FC Criterion: {e.name}"
        elif e in ULTIMATES:
            category = PointsCategory.FC_ULTIMATE
            description = f"FC Ultimate: {e.name}"
        else:
            tier_name = FC_CONFIG.current_submissions_tier.replace('_', '.')
            self.notes.append(f"{e.name} is not a tracked encounter for tier {tier_name}. \
                              No FC high-end content points awarded.")
            return

        if not full_or_partial_fc:
            self.notes.append(f"Not full or partial (4+) FC. FC members: {len(self.fc_members_in_fight)}. \
                              No FC high-end content points awarded.")
            return

        for member in self.fc_members_in_fight:
            self.points_events.append(
                PointsEvent(
                    uuid=str(uuid.uuid4()),
                    member_id=member.fcid,
                    points=category.points,
                    category=category,
                    description=description,
                    ts=int(time.time())
                )
            )

    def eval_vet_and_first_clears(self):
        # First clear: Vets and newbies get points
        e = self.fight_data.encounter
        if e not in CURRENT_SAVAGE_TO_POINTS_CATEGORY:
            tier_name = FC_CONFIG.current_submissions_tier.replace('_', '.')
            self.notes.append(f"{e.name} is not a tracked encounter for tier {tier_name}. \
                              No vet or first-time clear points awarded.")
            return

        veteran_members: List[Member] = []
        first_clear_members: List[Member] = []

        for member in self.fc_members_in_fight:
            clears: List[Clear] = FFLOGS_CLIENT.get_clears_for_member(member, [e])

            prior_clears: List[Clear] = [
                c for c in clears
                # Only count clears older than 1 minute ago from this clear - buffer added for safety
                if c.start_time < (self.fight_data.start_time - timedelta(seconds=60))
            ]

            if len(prior_clears) > 0:
                veteran_members.append(member)
            else:
                first_clear_members.append(member)

        category = CURRENT_SAVAGE_TO_POINTS_CATEGORY[e]
        for member in first_clear_members:
            # Extra check: If member has already been awarded one-time points, skip this one.
            member_points = DDB_CLIENT.get_member_points(member.fcid, tier=FC_CONFIG.current_submissions_tier)
            one_time_points_exist = member_points is not None and category in member_points['one_time']
            if one_time_points_exist:
                self.notes.append(f"{member.name} ({member.fcid}) has already been awarded points for {category.name}. Skipping.")
                continue

            self.points_events.append(
                PointsEvent(
                    uuid=str(uuid.uuid4()),
                    member_id=member.fcid,
                    points=category.points,
                    category=category,
                    description=f"First clear: {e.name}",
                    ts=int(time.time()),
                )
            )

        if len(first_clear_members) > 0:
            for member in veteran_members:
                self.points_events.append(
                    PointsEvent(
                        uuid=str(uuid.uuid4()),
                        member_id=member.fcid,
                        points=10,
                        category=PointsCategory.VET,
                        description=f"Veteran support: {e.name}",
                        ts=int(time.time()),
                    )
                )
        else:
            self.notes.append("No first-time clearees present. No veteran or first-time clear points awarded.")
