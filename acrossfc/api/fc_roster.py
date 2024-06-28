from typing import List

from acrossfc.core.model import Member
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT


def get_fc_roster():
    roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
    return [
        {
            'member_id': m.fcid,
            'name': m.name,
            'rank': m.rank
        }
        for m in roster
    ]


def get_member_id_by_name(name: str):
    roster: List[Member] = FFLOGS_CLIENT.get_fc_roster()
    name_parts = [p.strip() for p in name.split(' ')]
    for m in roster:
        fn, ln = m.name.split(' ')
        if name_parts[0] == fn and name_parts[1] == ln:
            return m.fcid

    return None
