# stdlib
from typing import List

# Local
from database import Database
from model import TrackedEncounter


def who_cleared_recently(database: Database, encounters: List[TrackedEncounter]):
    for encounter in encounters:
        encounter_clear_chart = database.get_clear_chart()[encounter]

        print()
        print(f'Who cleared {encounter.name} recently:')
        print('----------------------------------------------')

        clear_date_str = encounter_clear_chart[-1][0].isoformat()
        clearees = ", ".join(
            member.name
            for member in (encounter_clear_chart[-1][1] ^ encounter_clear_chart[-2][1])
        )
        print(f"{clear_date_str}: {clearees}")
