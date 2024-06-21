# stdlib
import uuid
import time
import logging
from typing import Optional, List

# Local
from acrossfc.core.model import (
    PointsEvent,
    Member,
    FFLogsFightData,
    PointsCategory,
    Clear
)
from acrossfc.core.constants import (
    POINTS,
    CURRENT_EXTREMES,
    CURRENT_UNREAL,
    CURRENT_SAVAGES,
    CURRENT_SAVAGE_TO_POINTS_CATEGORY,
    CURRENT_CRITERIONS,
    ULTIMATES
)
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT

LOG = logging.getLogger(__name__)


class PointsEvaluator:
    def __init__(self, fflogs_url: str, fc_pf_id: Optional[str]):
        self.fight_data: FFLogsFightData = FFLOGS_CLIENT.get_fight_data(fflogs_url)
        self.fc_roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
        self.fc_pf_id = fc_pf_id
        self.fc_members_in_fight: List[Member] = []
        self.points_events = []

        self.load_fc_member_ids()
        self.eval_fc_pf()
        self.eval_fc_high_end_content()
        self.eval_vet_and_first_clears()

        member_id_to_name_map = {
            m.fcid: m.name
            for m in self.fc_roster
        }
        for pe in self.points_events:
            LOG.debug(f"{member_id_to_name_map[pe.member_id]}: {pe.category.name} ({pe.points})")

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
        if self.fc_pf_id is not None:
            for member in self.fc_members_in_fight:
                category = PointsCategory.FC_PF
                self.points_events.append(
                    PointsEvent(
                        uuid=str(uuid.uuid4()),
                        member_id=member.fcid,
                        points=POINTS[category],
                        category=category,
                        description=f"FC PF: {self.fc_pf_id}",
                        ts=int(time.time()),
                        fc_pf_id=self.fc_pf_id
                    )
                )

    def eval_fc_high_end_content(self):
        """
        Participate in a Savage/Unreal/Extreme/Ultimate/Criterion
        Full or partial FC party (full-lockout or clear)
        STATICS DO NOT COUNT (10)
        """
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
            LOG.info("Not high end content. No points awarded for FC high end content.")
            return

        if not full_or_partial_fc:
            LOG.info(f"Not full or partial FC. FC members: {len(self.fc_members_in_fight)}")
            return

        for member in self.fc_members_in_fight:
            self.points_events.append(
                PointsEvent(
                    uuid=str(uuid.uuid4()),
                    member_id=member.fcid,
                    points=POINTS[category],
                    category=category,
                    description=description,
                    ts=int(time.time())
                )
            )

    def eval_vet_and_first_clears(self):
        veteran_members: List[Member] = []
        first_clear_members: List[Member] = []

        for member in self.fc_members_in_fight:
            clears: List[Clear] = FFLOGS_CLIENT.get_clears_for_member(member, [self.fight_data.encounter])

            current_clear: Clear = next(filter(lambda c: c.report_code == self.fight_data.report_id, clears))
            prior_clears: List[Clear] = [c for c in clears if c.start_time < current_clear.start_time]

            if len(prior_clears) > 0:
                veteran_members.append(member)
            else:
                first_clear_members.append(member)

        # First clear savage points
        if self.fight_data.encounter in CURRENT_SAVAGE_TO_POINTS_CATEGORY:
            category = CURRENT_SAVAGE_TO_POINTS_CATEGORY[self.fight_data.encounter]
            for member in first_clear_members:
                self.points_events.append(
                    PointsEvent(
                        uuid=str(uuid.uuid4()),
                        member_id=member.fcid,
                        points=POINTS[category],
                        category=category,
                        description=f"First clear: {self.fight_data.encounter.name}",
                        ts=int(time.time()),
                        fc_pf_id=self.fc_pf_id
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
                        description=f"Veteran support: {self.fight_data.encounter.name}",
                        ts=int(time.time()),
                        fc_pf_id=self.fc_pf_id
                    )
                )
