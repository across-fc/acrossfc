# stdlib
import logging
from typing import Optional, List

# Local
from acrossfc.core.model import PointEvent, Member, FFLogsFightData, PointsCategory, TrackedEncounter
from acrossfc.core.constants import (
    POINTS,
    CURRENT_EXTREMES,
    CURRENT_UNREAL,
    CURRENT_SAVAGES,
    CURRENT_CRITERIONS,
    ULTIMATES
)
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT

LOG = logging.getLogger(__name__)


class PointsEvaluator:
    def __init__(self, fflogs_url: str, fc_pf_id: Optional[str]):
        self.fight_data: FFLogsFightData = FFLOGS_CLIENT.get_fight_data(fflogs_url)
        self.fc_pf_id = fc_pf_id
        self.fc_member_ids = []
        self.point_events = []

        self.load_fc_member_ids()
        self.eval_fc_pf()
        self.eval_fc_high_end_content()
        self.eval_vet_and_first_clears()

    def load_fc_member_ids(self):
        fc_roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
        player_names_set = set(self.fight_data.player_names)
        for member in fc_roster:
            if member.name in player_names_set:
                self.fc_member_ids.append(member.fcid)
                player_names_set.remove(member.name)

        if len(player_names_set) > 0:
            LOG.debug(f"Skipping points registration for {player_names_set}: Not in FC roster")

    def eval_fc_pf(self):
        """
        Participate in ANY FC PF listing (10)
        """
        if self.fc_pf_id is not None:
            for user_id in self.fc_member_ids:
                category = PointsCategory.FC_PF
                self.point_events.append(
                    PointEvent(
                        member_id=user_id,
                        points=POINTS[category],
                        category=category,
                        description=f"FC PF: {self.fc_pf_id}"
                    )
                )

    def eval_fc_high_end_content(self):
        """
        Participate in a Savage/Unreal/Extreme/Ultimate/Criterion
        Full or partial FC party (full-lockout or clear)
        STATICS DO NOT COUNT (10)
        """
        full_or_partial_fc = (len(self.fc_member_ids) >= 4)

        # TODO: How to scan for statics? By frequency?

        def _match(encounter_list: List[TrackedEncounter]):
            for e in encounter_list:
                if (
                    self.fight_data.encounter_id == e.encounter_id and
                    (
                        e.difficulty_id is None or
                        self.fight_data.difficulty_id == e.difficulty_id
                    )
                ):
                    return e
            return None

        if (e := _match(CURRENT_EXTREMES)) is not None:
            category = PointsCategory.FC_EXTREME
            description = f"FC Extreme: {e.name}"
        elif (e := _match([CURRENT_UNREAL])) is not None:
            category = PointsCategory.FC_UNREAL
            description = f"FC Unreal: {e.name}"
        elif (e := _match(CURRENT_SAVAGES)) is not None:
            category = PointsCategory.FC_SAVAGE
            description = f"FC Savage: {e.name}"
        elif (e := _match(CURRENT_CRITERIONS)) is not None:
            category = PointsCategory.FC_CRITERION
            description = f"FC Criterion: {e.name}"
        elif (e := _match(ULTIMATES)) is not None:
            category = PointsCategory.FC_ULTIMATE
            description = f"FC Ultimate: {e.name}"
        else:
            LOG.info("Not high end content. No points awarded for FC high end content.")
            return

        if not full_or_partial_fc:
            LOG.info(f"Not full or partial FC. FC members: {len(self.fc_member_ids)}")
            return

        for member_id in self.fc_member_ids:
            self.point_events.append(
                PointEvent(
                    member_id=member_id,
                    points=POINTS[category],
                    category=category,
                    description=description,
                )
            )

    def eval_vet_and_first_clears(self):
        # TODO: Insert all the point events
        # POINTS = {
        #     PointsCategory.VET: 10,
        #     # one-time
        #     PointsCategory.SAVAGE_1: 10,
        #     PointsCategory.SAVAGE_2: 10,
        #     PointsCategory.SAVAGE_3: 10,
        #     PointsCategory.SAVAGE_4_1: 10,
        #     PointsCategory.SAVAGE_4_2: 10,
        # }
        pass
