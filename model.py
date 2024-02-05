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


class Job(Enum):
    MRD = 'Marauder'
    WAR = 'Warrior'
    GLA = 'Gladiator'
    PLD = 'Paladin'
    DRK = 'DarkKnight'
    GNB = 'Gunbreaker'
    CNJ = 'Conjurer'
    WHM = 'WhiteMage'
    ACN = 'Arcanist'
    SCH = 'Scholar'
    AST = 'Astrologian'
    SGE = 'Sage'
    LNC = 'Lancer'
    DRG = 'Dragoon'
    PGL = 'Pugilist'
    MNK = 'Monk'
    ROG = 'Rogue'
    NIN = 'Ninja'
    SAM = 'Samurai'
    RPR = 'Reaper'
    ARC = 'Archer'
    BRD = 'Bard'
    MCH = 'Machinist'
    DNC = 'Dancer'
    THM = 'Thaumaturge'
    BLM = 'BlackMage'
    SMN = 'Summoner'
    RDM = 'RedMage'
    BLU = 'BlueMage'


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
