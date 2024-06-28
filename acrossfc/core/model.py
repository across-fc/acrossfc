# stdlib
from datetime import datetime
from typing import Optional, NamedTuple, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum

# 3rd-party
from peewee import (
    Model,
    IntegerField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    FloatField,
    BooleanField,
)


# -----------------------------------------------
# ClearDB peewee models
# -----------------------------------------------

class Member(Model):
    fcid = IntegerField(primary_key=True)
    name = CharField(255)
    rank = IntegerField()


class TrackedEncounter(Model):
    id = CharField(16, primary_key=True)
    name = CharField(16)
    encounter_id = IntegerField()
    difficulty_id = IntegerField(null=True)
    partition_id = IntegerField(null=True)
    with_echo = BooleanField(default=False)

    class Meta:
        indexes = ((("encounter_id", "difficulty_id", "partition_id"), True),)

    def __str__(self):
        return f"{self.name}_{self.encounter_id}_{self.difficulty_id}_{self.partition_id}"

    def __repr__(self):
        return str(self)


TrackedEncounterName = str


class JobCategory(Model):
    name = CharField(32, primary_key=True)
    long_name = CharField(64)


class Job(Model):
    tla = CharField(3, primary_key=True)
    name = CharField(64)
    main_category = ForeignKeyField(JobCategory)
    sub_category = ForeignKeyField(JobCategory, null=True)


class Clear(Model):
    member = ForeignKeyField(Member)
    encounter = ForeignKeyField(TrackedEncounter)
    start_time = DateTimeField()
    historical_pct = FloatField()
    report_code = CharField(32)
    report_fight_id = IntegerField()
    job = ForeignKeyField(Job)
    locked_in = BooleanField()


# -----------------------------------------------
# DynamoDB submissions / points models
# -----------------------------------------------

class PointsCategory(Enum):
    FC_PF = 100
    MENTOR_TICKET = 102
    FC_STATIC = 103
    FC_EXTREME = 200
    FC_UNREAL = 201
    FC_SAVAGE = 202
    FC_CRITERION = 203
    FC_CRITERION_SAVAGE = 204
    FC_ULTIMATE = 205
    SAVAGE_1 = 310
    SAVAGE_2 = 320
    SAVAGE_3 = 330
    SAVAGE_4_1 = 340
    SAVAGE_4_2 = 341
    VET = 400
    CRAFTING_GATHERING = 401
    MENTOR = 402
    AD_HOC = 777

    @property
    def description(self):
        descriptions = {
            self.FC_PF: "FC PF Listing",
            self.MENTOR_TICKET: "Put in and finish a mentor ticket",
            self.FC_STATIC: "Be a part of a full / partial FC Savage / Ultimate static",
            self.FC_EXTREME: "FC EX party",
            self.FC_UNREAL: "FC Unreal party",
            self.FC_SAVAGE: "FC Savage party",
            self.FC_CRITERION: "FC Criterion party",
            self.FC_CRITERION_SAVAGE: "FC Criterion Savage party",
            self.FC_ULTIMATE: "FC Ultimate party",
            self.SAVAGE_1: "Clear the first floor of Savage",
            self.SAVAGE_2: "Clear the second floor of Savage",
            self.SAVAGE_3: "Clear the third floor of Savage",
            self.SAVAGE_4_1: "Clear the door boos on the fourth floor of Savage",
            self.SAVAGE_4_2: "Clear the fourth floor of Savage",
            self.VET: "Veteran award: Helping with a first-clear",
            self.CRAFTING_GATHERING: "Crafting / Gathering team member",
            self.MENTOR: "Mentor",
            self.AD_HOC: "Ad hoc"
        }
        return descriptions[self]

    @property
    def constraints(self):
        constraints = {
            self.FC_EXTREME: "4+ FC, non-static",
            self.FC_UNREAL: "4+ FC, non-static",
            self.FC_SAVAGE: "4+ FC, non-static",
            self.FC_CRITERION: "4+ FC, non-static",
            self.FC_CRITERION_SAVAGE: "4+ FC, non-static",
            self.FC_ULTIMATE: "4+ FC, non-static",
            self.SAVAGE_1: "One-time only",
            self.SAVAGE_2: "One-time only",
            self.SAVAGE_3: "One-time only",
            self.SAVAGE_4_1: "One-time only",
            self.SAVAGE_4_2: "One-time only",
        }
        return constraints.get(self, None)

    @property
    def points(self):
        points = {
            self.FC_PF: 10,
            self.MENTOR_TICKET: 10,
            self.FC_STATIC: 20,
            self.FC_EXTREME: 10,
            self.FC_UNREAL: 10,
            self.FC_SAVAGE: 10,
            self.FC_CRITERION: 10,
            self.FC_CRITERION_SAVAGE: 10,
            self.FC_ULTIMATE: 10,
            self.SAVAGE_1: 10,
            self.SAVAGE_2: 10,
            self.SAVAGE_3: 10,
            self.SAVAGE_4_1: 10,
            self.SAVAGE_4_2: 10,
            self.VET: 10,
            self.CRAFTING_GATHERING: 50,
            self.MENTOR: 25,
            self.AD_HOC: None
        }
        return points[self]

    @property
    def is_one_time(self):
        one_time_points = [
            self.SAVAGE_1,
            self.SAVAGE_2,
            self.SAVAGE_3,
            self.SAVAGE_4_1,
            self.SAVAGE_4_2,
            self.CRAFTING_GATHERING,
            self.MENTOR
        ]
        return self in one_time_points


class PointsEventStatus(Enum):
    PENDING = 0
    APPROVED = 1
    DENIED = 2
    ONE_TIME_POINTS_ALREADY_AWARDED = 3


@dataclass
class PointsEvent:
    uuid: str
    member_id: int
    points: int
    category: PointsCategory
    description: str
    ts: int
    submission_uuid: Optional[str] = None
    status: PointsEventStatus = PointsEventStatus.PENDING

    def __repr__(self):
        return f"{self.member_id}: {self.category.name} ({self.points})"

    def to_user_json(self):
        ret = asdict(self)
        ret['category'] = self.category.value
        # Keep submission ID but remove status
        del ret['status']
        return ret

    def to_submission_json(self):
        ret = asdict(self)
        ret['category'] = self.category.value
        # Keep status but remove submissions ID
        ret['status'] = self.status.value
        del ret['submission_uuid']
        return ret


class SubmissionsChannel(Enum):
    FC_PF = 1
    FC_BOT_FFLOGS = 2
    FC_BOT_SCREENSHOT = 3
    FC_BOT_ADMIN = 4
    ADMIN_PORTAL = 5
    DEV = 777


# -----------------------------------------------
# Convenience structs and aliases
# -----------------------------------------------

class ClearRate(NamedTuple):
    clears: int
    eligible_members: int

    @property
    def clear_rate(self):
        return self.clears / self.eligible_members


class FFLogsFightData(NamedTuple):
    report_id: str
    encounter: TrackedEncounter
    start_time: datetime
    player_names: List[str]

    @property
    def fight_signature(self):
        """
        Used to identify potential duplicate submissions.
        If it's by the same people in the same fight, it might be a dupe.
        """
        return hash(
            tuple(
                sorted(self.player_names) + [
                    self.encounter.encounter_id,
                    self.encounter.difficulty_id
                ]
            )
        )


class CommandConfig(NamedTuple):
    func: Callable
    help: str
    decorators: List[Callable] = []
    # e.g.
    # [
    #     click.option(...),
    #     click.option(...),
    #     click.pass_context,
    #     ...
    # ]
