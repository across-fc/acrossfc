# stdlib
from itertools import groupby
from collections import defaultdict
from typing import List, Dict, NamedTuple

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


# -------------------------
# Convenience structs and aliases
# -------------------------


class ClearRate(NamedTuple):
    clears: int
    eligible_members: int

    @property
    def clear_rate(self):
        return self.clears / self.eligible_members


TrackedEncounterName = str
TierName = str

# -------------------------
# Constant data
# -------------------------


def create(cls, *args):
    """Shorthand for creating a new model object with the given arguments, assuming they are given in field order."""
    fields = list(cls._meta.fields.keys())
    return cls(**{
        fields[i]: args[i]
        for i in range(len(args))
    })


ALL_MODELS = [Member, TrackedEncounter, JobCategory, Job, Clear]

# Anabaseios

P9S = create(TrackedEncounter, "P9S", "P9S", 88, 101)
P9S_ECHO = create(TrackedEncounter, "P9S_ECHO", "P9S", 88, 101, 13, True)
P10S = create(TrackedEncounter, "P10S", "P10S", 89, 101)
P10S_ECHO = create(TrackedEncounter, "P10S_ECHO", "P10S", 89, 101, 13, True)
P11S = create(TrackedEncounter, "P11S", "P11S", 90, 101)
P11S_ECHO = create(TrackedEncounter, "P11S_ECHO", "P11S", 90, 101, 13, True)
P12S_P1 = create(TrackedEncounter, "P12S_P1", "P12S_P1", 91, 101)
P12S_P1_ECHO = create(TrackedEncounter, "P12S_P1_ECHO", "P12S_P1", 91, 101, 13, True)
P12S = create(TrackedEncounter, "P12S", "P12S", 92, 101)
P12S_ECHO = create(TrackedEncounter, "P12S_ECHO", "P12S", 92, 101, 13, True)

# Ultimates

UWU_EW = create(TrackedEncounter, "UWU_EW", "UWU", 1061)
UWU_SHB = create(TrackedEncounter, "UWU_SHB", "UWU", 1048)
UWU_SB = create(TrackedEncounter, "UWU_SB", "UWU", 1042)

UCOB_EW = create(TrackedEncounter, "UCOB_EW", "UCOB", 1060)
UCOB_SHB = create(TrackedEncounter, "UCOB_SHB", "UCOB", 1047)
UCOB_SB = create(TrackedEncounter, "UCOB_SB", "UCOB", 1039)

TEA_EW = create(TrackedEncounter, "TEA_EW", "TEA", 1062)
TEA_SHB = create(TrackedEncounter, "TEA_SHB", "TEA", 1050)

DSR_EW = create(TrackedEncounter, "DSR_EW", "DSR", 1065)

TOP_EW = create(TrackedEncounter, "TOP_EW", "TOP", 1068)

ALL_TRACKED_ENCOUNTERS = [
    P9S, P9S_ECHO,
    P10S, P10S_ECHO,
    P11S, P11S_ECHO,
    P12S_P1, P12S_P1_ECHO,
    P12S, P12S_ECHO,
    UWU_EW,
    UWU_SHB,
    UWU_SB,
    UCOB_EW,
    UCOB_SHB,
    UCOB_SB,
    TEA_EW,
    TEA_SHB,
    DSR_EW,
    TOP_EW,
]
ALL_TRACKED_ENCOUNTER_NAMES = list(name for name, _ in groupby(ALL_TRACKED_ENCOUNTERS, key=lambda e: e.name))

# For now, they are they same. In the future we may only track a subset of encounters.
ACTIVE_TRACKED_ENCOUNTERS = ALL_TRACKED_ENCOUNTERS
ACTIVE_TRACKED_ENCOUNTER_NAMES = list(name for name, _ in groupby(ACTIVE_TRACKED_ENCOUNTERS, key=lambda e: e.name))

TIER_NAME_TO_ENCOUNTER_NAMES_MAP: Dict[TierName, List[TrackedEncounterName]] = {
    "ANABASEIOS": [
        "P9S",
        "P10S",
        "P11S",
        "P12S_P1",
        "P12S",
    ],
    "ULTIMATE": [
        "UWU",
        "UCOB",
        "TEA",
        "DSR",
        "TOP",
    ],
}

TANK = JobCategory(name="TANK", long_name="Tank")
HEALER = JobCategory(name="HEALER", long_name="Healer")
REGEN_HEALER = JobCategory(name="REGEN_HEALER", long_name="Regen Healer")
SHIELD_HEALER = JobCategory(name="SHIELD_HEALER", long_name="Shield Healer")
DPS = JobCategory(name="DPS", long_name="DPS")
MELEE_DPS = JobCategory(name="MELEE_DPS", long_name="Melee DPS")
PRANGED_DPS = JobCategory(name="PRANGED_DPS", long_name="Physical Ranged DPS")
CASTER_DPS = JobCategory(name="CASTER_DPS", long_name="Caster DPS")

JOB_CATEGORIES = [
    TANK,
    HEALER,
    REGEN_HEALER,
    SHIELD_HEALER,
    DPS,
    MELEE_DPS,
    PRANGED_DPS,
    CASTER_DPS,
]

NAME_TO_JOB_CATEGORIES_MAP = {c.name: c for c in JOB_CATEGORIES}

MRD = Job(tla="MRD", name="Marauder", main_category=TANK.name, sub_category=None)
WAR = Job(tla="WAR", name="Warrior", main_category=TANK.name, sub_category=None)
GLA = Job(tla="GLA", name="Gladiator", main_category=TANK.name, sub_category=None)
PLD = Job(tla="PLD", name="Paladin", main_category=TANK.name, sub_category=None)
DRK = Job(tla="DRK", name="DarkKnight", main_category=TANK.name, sub_category=None)
GNB = Job(tla="GNB", name="Gunbreaker", main_category=TANK.name, sub_category=None)
CNJ = Job(tla="CNJ", name="Conjurer", main_category=HEALER.name, sub_category=REGEN_HEALER.name)
WHM = Job(tla="WHM", name="WhiteMage", main_category=HEALER.name, sub_category=REGEN_HEALER.name)
SCH = Job(tla="SCH", name="Scholar", main_category=HEALER.name, sub_category=SHIELD_HEALER.name)
AST = Job(tla="AST", name="Astrologian", main_category=HEALER.name, sub_category=REGEN_HEALER.name)
SGE = Job(tla="SGE", name="Sage", main_category=HEALER.name, sub_category=SHIELD_HEALER.name)
LNC = Job(tla="LNC", name="Lancer", main_category=DPS.name, sub_category=MELEE_DPS.name)
DRG = Job(tla="DRG", name="Dragoon", main_category=DPS.name, sub_category=MELEE_DPS.name)
PGL = Job(tla="PGL", name="Pugilist", main_category=DPS.name, sub_category=MELEE_DPS.name)
MNK = Job(tla="MNK", name="Monk", main_category=DPS.name, sub_category=MELEE_DPS.name)
ROG = Job(tla="ROG", name="Rogue", main_category=DPS.name, sub_category=MELEE_DPS.name)
NIN = Job(tla="NIN", name="Ninja", main_category=DPS.name, sub_category=MELEE_DPS.name)
SAM = Job(tla="SAM", name="Samurai", main_category=DPS.name, sub_category=MELEE_DPS.name)
RPR = Job(tla="RPR", name="Reaper", main_category=DPS.name, sub_category=MELEE_DPS.name)
ARC = Job(tla="ARC", name="Archer", main_category=DPS.name, sub_category=PRANGED_DPS.name)
BRD = Job(tla="BRD", name="Bard", main_category=DPS.name, sub_category=PRANGED_DPS.name)
MCH = Job(tla="MCH", name="Machinist", main_category=DPS.name, sub_category=PRANGED_DPS.name)
DNC = Job(tla="DNC", name="Dancer", main_category=DPS.name, sub_category=PRANGED_DPS.name)
THM = Job(tla="THM", name="Thaumaturge", main_category=DPS.name, sub_category=CASTER_DPS.name)
BLM = Job(tla="BLM", name="BlackMage", main_category=DPS.name, sub_category=CASTER_DPS.name)
ACN = Job(tla="ACN", name="Arcanist", main_category=DPS.name, sub_category=CASTER_DPS.name)
SMN = Job(tla="SMN", name="Summoner", main_category=DPS.name, sub_category=CASTER_DPS.name)
RDM = Job(tla="RDM", name="RedMage", main_category=DPS.name, sub_category=CASTER_DPS.name)
BLU = Job(tla="BLU", name="BlueMage", main_category=DPS.name, sub_category=CASTER_DPS.name)

JOBS = [
    MRD, WAR,
    GLA, PLD,
    DRK,
    GNB,
    CNJ, WHM,
    SCH,
    AST,
    SGE,
    LNC, DRG,
    PGL, MNK,
    ROG, NIN,
    SAM,
    RPR,
    ARC, BRD,
    MCH,
    DNC,
    THM, BLM,
    ACN, SMN,
    RDM,
    BLU,
]

NAME_TO_JOB_MAP = {job.name: job for job in JOBS}

TLA_TO_JOB_MAP = {job.tla: job for job in JOBS}
