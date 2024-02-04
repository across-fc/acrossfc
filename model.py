from enum import Enum
from typing import List, Dict, NamedTuple, Optional

class FFL_Zone(Enum):
    ANABASEIOS= 54
    ABYSSOS = 49

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

class Tier(NamedTuple):
    zone: FFL_Zone
    difficulty: FFL_Difficulty

class TrackedEncounter(NamedTuple):
    name: str
    boss: FFL_Boss
    difficulty: Optional[FFL_Difficulty]

class GuildMember(NamedTuple):
    id: int
    name: str
    rank: int

# All the encounters we want to track
TRACKED_ENCOUNTERS: List[TrackedEncounter] = [
    TrackedEncounter('P9S', FFL_Boss.KOKYTOS, FFL_Difficulty.SAVAGE),
    TrackedEncounter('P10S', FFL_Boss.PANDAEMONIUM, FFL_Difficulty.SAVAGE),
    TrackedEncounter('P11S', FFL_Boss.THEMIS, FFL_Difficulty.SAVAGE),
    TrackedEncounter('P12S (P1)', FFL_Boss.ATHENA, FFL_Difficulty.SAVAGE),
    TrackedEncounter('P12S', FFL_Boss.PALLAS_ATHENA, FFL_Difficulty.SAVAGE),
    TrackedEncounter('TOP', FFL_Boss.TOP, None),
    TrackedEncounter('DSR', FFL_Boss.DSR, None),
    TrackedEncounter('TEA', FFL_Boss.TEA, None),
    TrackedEncounter('UWU', FFL_Boss.UWU, None),
    TrackedEncounter('UCOB', FFL_Boss.UCOB, None),
]