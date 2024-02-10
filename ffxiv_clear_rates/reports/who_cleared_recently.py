# stdlib
from io import StringIO
from typing import List
from datetime import date

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter
from .report import Report


def who_cleared_recently(database: Database, encounters: List[TrackedEncounter]) -> Report:
    buffer = StringIO()

    for i, encounter in enumerate(encounters):
        if i > 0:
            buffer.write('\n\n')

        encounter_clear_chart = database.get_clear_chart()[encounter]

        buffer.write(encounter.name)
        buffer.write('\n----------------------------------------------\n')

        clear_date_str = encounter_clear_chart[-1][0].isoformat()
        clearees = ", ".join(
            member.name
            for member in (encounter_clear_chart[-1][1] ^ encounter_clear_chart[-2][1])
        )
        buffer.write(f"{clear_date_str}: {clearees}")

    return Report(
        ':white_check_mark:',
        f'Who cleared recently: {date.today()}',
        None,
        buffer.getvalue(),
        None
    )