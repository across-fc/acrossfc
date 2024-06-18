# stdlib
from itertools import groupby
from typing import Dict, List

# Local
from .model import (
    Member,
    Clear,
    TrackedEncounter,
    Job,
    JobCategory,
    PointsCategory,
    TierName,
    TrackedEncounterName
)


def create(cls, *args):
    """Shorthand for creating a new model object with the given arguments, assuming they are given in field order."""
    fields = list(cls._meta.fields.keys())
    return cls(**{
        fields[i]: args[i]
        for i in range(len(args))
    })


ALL_MODELS = [Member, TrackedEncounter, JobCategory, Job, Clear]

# -----------------------------------------
# Encounters
# -----------------------------------------

# Extremes

EW_EX_7 = create(TrackedEncounter, "EW_EX_7", "ZEROMUS", 1070)
EW_EX_6 = create(TrackedEncounter, "EW_EX_6", "GOLBEZ", 1069)
EW_EX_5 = create(TrackedEncounter, "EW_EX_5", "RUBICANTE", 1067)
EW_EX_4 = create(TrackedEncounter, "EW_EX_4", "BARBARICCIA", 1066)
EW_EX_3 = create(TrackedEncounter, "EW_EX_3", "ENDSINGER", 1063)
EW_EX_2 = create(TrackedEncounter, "EW_EX_2", "HYDAELYN", 1059)
EW_EX_1 = create(TrackedEncounter, "EW_EX_1", "ZODIARK", 1058)

CURRENT_EXTREMES = [
    EW_EX_7,
    EW_EX_6,
    EW_EX_5,
    EW_EX_4,
    EW_EX_3,
    EW_EX_2,
    EW_EX_1,
]

# Unreal

EW_UNREAL_5 = create(TrackedEncounter, "EW_UNREAL_5", "THORDAN", 3008)
EW_UNREAL_4 = create(TrackedEncounter, "EW_UNREAL_4", "ZURVAN", 3007)
EW_UNREAL_3 = create(TrackedEncounter, "EW_UNREAL_3", "SOPHIA", 3006)
EW_UNREAL_2 = create(TrackedEncounter, "EW_UNREAL_2", "SEPHIROT", 3005)
EW_UNREAL_1 = create(TrackedEncounter, "EW_UNREAL_1", "ULTIMA", 3004)

CURRENT_UNREAL = EW_UNREAL_5

# Savage: Anabaseios

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

CURRENT_SAVAGES = [
    P9S, P9S_ECHO,
    P10S, P10S_ECHO,
    P11S, P11S_ECHO,
    P12S_P1, P12S_P1_ECHO,
    P12S, P12S_ECHO
]

# Criterion

EW_CRIT_3 = create(TrackedEncounter, "EW_CRIT_3", "AAI", 4538, 10)
EW_CRIT_2 = create(TrackedEncounter, "EW_CRIT_2", "AMR", 4536, 10)
EW_CRIT_1 = create(TrackedEncounter, "EW_CRIT_1", "ASS", 4533, 10)

CURRENT_CRITERIONS = [
    EW_CRIT_1, EW_CRIT_2, EW_CRIT_3
]

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

ULTIMATES = [
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
ULTIMATE_NAMES = list(name for name, _ in groupby(ULTIMATES, key=lambda e: e.name))

ALL_ENCOUNTERS = CURRENT_EXTREMES + CURRENT_SAVAGES + [CURRENT_UNREAL] + CURRENT_CRITERIONS + ULTIMATES
ALL_ENCOUNTER_NAMES = list(name for name, _ in groupby(ALL_ENCOUNTERS, key=lambda e: e.name))

# Not tracking clear rates for EXs
TRACKED_ENCOUNTERS = CURRENT_SAVAGES + ULTIMATES
TRACKED_ENCOUNTER_NAMES = list(name for name, _ in groupby(TRACKED_ENCOUNTERS, key=lambda e: e.name))

TIER_NAME_TO_ENCOUNTER_NAMES_MAP: Dict[TierName, List[TrackedEncounterName]] = {
    "ANABASEIOS": [
        "P9S",
        "P10S",
        "P11S",
        "P12S_P1",
        "P12S",
    ],
    "ULTIMATE": [
        "UCOB",
        "UWU",
        "TEA",
        "DSR",
        "TOP",
    ],
}

# -----------------------------------------
# Jobs
# -----------------------------------------

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

# -----------------------------------------
# FC Participation points
# -----------------------------------------

POINTS = {
    PointsCategory.FC_PF: 10,
    PointsCategory.FC_EVENT: 20,
    PointsCategory.MENTOR_TICKET: 10,
    PointsCategory.FC_STATIC: 20,
    PointsCategory.FC_EXTREME: 10,
    PointsCategory.FC_UNREAL: 10,
    PointsCategory.FC_SAVAGE: 10,
    PointsCategory.FC_CRITERION: 10,
    PointsCategory.FC_CRITERION_SAVAGE: 10,
    PointsCategory.FC_ULTIMATE: 10,
    PointsCategory.SAVAGE_1: 10,
    PointsCategory.SAVAGE_2: 10,
    PointsCategory.SAVAGE_3: 10,
    PointsCategory.SAVAGE_4_1: 10,
    PointsCategory.SAVAGE_4_2: 10,
    PointsCategory.VET: 10,
    PointsCategory.CRAFTING_GATHERING: 50,
    PointsCategory.MENTOR: 25
}
