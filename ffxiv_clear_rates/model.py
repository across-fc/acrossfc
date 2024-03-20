# stdlib
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
    name = CharField(16)
    encounter_id = IntegerField()
    difficulty_id = IntegerField(null=True)
    partition_id = IntegerField(null=True)

    class Meta:
        indexes = ((("encounter_id", "difficulty_id", "partition_id"), True),)


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

# -------------------------
# Constant data
# -------------------------

ALL_MODELS = [Member, TrackedEncounter, JobCategory, Job, Clear]

# Anabaseios

P9S = TrackedEncounter(name="P9S", encounter_id=88, difficulty_id=101)
P9S_ECHO = TrackedEncounter(name="P9S", encounter_id=88, difficulty_id=101, partition_id=13)

P10S = TrackedEncounter(name="P10S", encounter_id=89, difficulty_id=101)
P10S_ECHO = TrackedEncounter(name="P10S", encounter_id=89, difficulty_id=101, partition_id=13)

P11S = TrackedEncounter(name="P11S", encounter_id=90, difficulty_id=101)
P11S_ECHO = TrackedEncounter(name="P11S", encounter_id=90, difficulty_id=101, partition_id=13)

P12S_P1 = TrackedEncounter(name="P12S_P1", encounter_id=91, difficulty_id=101)
P12S_P1_ECHO = TrackedEncounter(name="P12S_P1", encounter_id=91, difficulty_id=101, partition_id=13)

P12S = TrackedEncounter(name="P12S", encounter_id=92, difficulty_id=101)
P12S_ECHO = TrackedEncounter(name="P12S", encounter_id=92, difficulty_id=101, partition_id=13)

# Ultimates

UWU_EW = TrackedEncounter(name="UWU", encounter_id=1061)
UWU_SHB = TrackedEncounter(name="UWU", encounter_id=1048)
UWU_SB = TrackedEncounter(name="UWU", encounter_id=1042)

UCOB_EW = TrackedEncounter(name="UCOB", encounter_id=1060)
UCOB_SHB = TrackedEncounter(name="UCOB", encounter_id=1047)
UCOB_SB = TrackedEncounter(name="UCOB", encounter_id=1039)

TEA_EW = TrackedEncounter(name="TEA", encounter_id=1062)
TEA_SHB = TrackedEncounter(name="TEA", encounter_id=1050)

DSR_EW = TrackedEncounter(name="DSR", encounter_id=1065)

TOP_EW = TrackedEncounter(name="TOP", encounter_id=1068)

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

NAME_TO_TRACKED_ENCOUNTER_LIST_MAP = defaultdict(list)
for te in ALL_TRACKED_ENCOUNTERS:
    NAME_TO_TRACKED_ENCOUNTER_LIST_MAP[te.name].append(te)

TIER_NAME_TO_TRACKED_ENCOUNTERS_MAP: Dict[str, List[TrackedEncounter]] = {
    "ANABASEIOS": [
        P9S, P9S_ECHO,
        P10S, P10S_ECHO,
        P11S, P11S_ECHO,
        P12S_P1, P12S_P1_ECHO,
        P12S, P12S_ECHO,
    ],
    "ULTIMATE": [
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
