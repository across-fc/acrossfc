# stdlib
from datetime import datetime
from enum import Enum
from typing import List, NamedTuple, Optional


class FFL_Boss(Enum):
    # Also known as 'encounter' in the FFLogs API
    KOKYTOS = 88
    PANDAEMONIUM = 89
    THEMIS = 90
    ATHENA = 91
    PALLAS_ATHENA = 92
    TOP = 1068
    DSR = 1065
    TEA = 1062
    UWU = 1061
    UCOB = 1060


class FFL_Difficulty(Enum):
    SAVAGE = 101
    NORMAL = 100


class TrackedEncounter(NamedTuple):
    name: str
    boss: FFL_Boss
    difficulty: Optional[FFL_Difficulty]


class GuildMember(NamedTuple):
    id: int
    name: str
    rank: int


class JobCategory(Enum):
    TANK = 'Tank'
    HEALER = 'Healer'
    REGEN_HEALER = 'Regen Healer'
    SHIELD_HEALER = 'Shield Healer'
    DPS = 'DPS'
    MELEE_DPS = 'Melee DPS'
    PRANGED_DPS = 'Physical Ranged DPS'
    CASTER_DPS = 'Caster DPS'


class Job(NamedTuple):
    name: str
    acronym: str
    main_category: JobCategory
    sub_category: Optional[JobCategory]


class Clear(NamedTuple):
    member: GuildMember
    encounter: TrackedEncounter
    start_time: datetime
    historical_pct: float
    report_code: str
    report_fight_id: int
    spec: Job
    locked_in: bool


class ClearRate(NamedTuple):
    clears: int
    eligible_members: int

    @property
    def clear_rate(self):
        return self.clears / self.eligible_members


# All the encounters we want to track
P9S = TrackedEncounter('P9S', FFL_Boss.KOKYTOS, FFL_Difficulty.SAVAGE)
P10S = TrackedEncounter('P10S', FFL_Boss.PANDAEMONIUM, FFL_Difficulty.SAVAGE)
P11S = TrackedEncounter('P11S', FFL_Boss.THEMIS, FFL_Difficulty.SAVAGE)
P12S_P1 = TrackedEncounter('P12S (P1)', FFL_Boss.ATHENA, FFL_Difficulty.SAVAGE)
P12S = TrackedEncounter('P12S', FFL_Boss.PALLAS_ATHENA, FFL_Difficulty.SAVAGE)
TOP = TrackedEncounter('TOP', FFL_Boss.TOP, None)
DSR = TrackedEncounter('DSR', FFL_Boss.DSR, None)
TEA = TrackedEncounter('TEA', FFL_Boss.TEA, None)
UWU = TrackedEncounter('UWU', FFL_Boss.UWU, None)
UCOB = TrackedEncounter('UCOB', FFL_Boss.UCOB, None)

TRACKED_ENCOUNTERS: List[TrackedEncounter] = [
    P9S,
    P10S,
    P11S,
    P12S_P1,
    P12S,
    TOP,
    DSR,
    TEA,
    UWU,
    UCOB,
]

MRD = Job('Marauder', 'MRD', JobCategory.TANK, None)
WAR = Job('Warrior', 'WAR', JobCategory.TANK, None)
GLA = Job('Gladiator', 'GLA', JobCategory.TANK, None)
PLD = Job('Paladin', 'PLD', JobCategory.TANK, None)
DRK = Job('DarkKnight', 'DRK', JobCategory.TANK, None)
GNB = Job('Gunbreaker', 'GNB', JobCategory.TANK, None)
CNJ = Job('Conjurer', 'CNJ', JobCategory.HEALER, JobCategory.REGEN_HEALER)
WHM = Job('WhiteMage', 'WHM', JobCategory.HEALER, JobCategory.REGEN_HEALER)
SCH = Job('Scholar', 'SCH', JobCategory.HEALER, JobCategory.SHIELD_HEALER)
AST = Job('Astrologian', 'AST', JobCategory.HEALER, JobCategory.REGEN_HEALER)
SGE = Job('Sage', 'SGE', JobCategory.HEALER, JobCategory.SHIELD_HEALER)
LNC = Job('Lancer', 'LNC', JobCategory.DPS, JobCategory.MELEE_DPS)
DRG = Job('Dragoon', 'DRG', JobCategory.DPS, JobCategory.MELEE_DPS)
PGL = Job('Pugilist', 'PGL', JobCategory.DPS, JobCategory.MELEE_DPS)
MNK = Job('Monk', 'MNK', JobCategory.DPS, JobCategory.MELEE_DPS)
ROG = Job('Rogue', 'ROG', JobCategory.DPS, JobCategory.MELEE_DPS)
NIN = Job('Ninja', 'NIN', JobCategory.DPS, JobCategory.MELEE_DPS)
SAM = Job('Samurai', 'SAM', JobCategory.DPS, JobCategory.MELEE_DPS)
RPR = Job('Reaper', 'RPR', JobCategory.DPS, JobCategory.MELEE_DPS)
ARC = Job('Archer', 'ARC', JobCategory.DPS, JobCategory.PRANGED_DPS)
BRD = Job('Bard', 'BRD', JobCategory.DPS, JobCategory.PRANGED_DPS)
MCH = Job('Machinist', 'MCH', JobCategory.DPS, JobCategory.PRANGED_DPS)
DNC = Job('Dancer', 'DNC', JobCategory.DPS, JobCategory.PRANGED_DPS)
THM = Job('Thaumaturge', 'THM', JobCategory.DPS, JobCategory.CASTER_DPS)
BLM = Job('BlackMage', 'BLM', JobCategory.DPS, JobCategory.CASTER_DPS)
ACN = Job('Arcanist', 'ACN', JobCategory.DPS, JobCategory.CASTER_DPS)
SMN = Job('Summoner', 'SMN', JobCategory.DPS, JobCategory.CASTER_DPS)
RDM = Job('RedMage', 'RDM', JobCategory.DPS, JobCategory.CASTER_DPS)
BLU = Job('BlueMage', 'BLU', JobCategory.DPS, JobCategory.CASTER_DPS)

JOBS = [
    MRD,
    WAR,
    GLA,
    PLD,
    DRK,
    GNB,
    CNJ,
    WHM,
    SCH,
    AST,
    SGE,
    LNC,
    DRG,
    PGL,
    MNK,
    ROG,
    NIN,
    SAM,
    RPR,
    ARC,
    BRD,
    MCH,
    DNC,
    THM,
    BLM,
    ACN,
    SMN,
    RDM,
    BLU
]
