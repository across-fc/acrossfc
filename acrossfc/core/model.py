# stdlib
from typing import Optional, NamedTuple, Callable, List
from dataclasses import dataclass
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
    FC_EVENT = 101
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


@dataclass
class PointsEvent:
    uuid: str
    member_id: int
    points: int
    category: PointsCategory
    description: str
    ts: int
    submission_uuid: Optional[str]
    fc_pf_id: Optional[str]
    approved: Optional[bool]
    reviewed_by: Optional[int]

    def __repr__(self):
        return f"{self.member_id}: {self.category.name} ({self.points})"


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
    encounter_id: int
    difficulty_id: int
    player_names: List[str]


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
