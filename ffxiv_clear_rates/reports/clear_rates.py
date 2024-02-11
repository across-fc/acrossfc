# stdlib
from typing import Dict
from datetime import date

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounterName, ClearRate, TRACKED_ENCOUNTERS
from .report import Report


class ClearRates(Report):
    def __init__(self, database: Database):
        clear_rates: Dict[TrackedEncounterName, ClearRate] = database.get_clear_rates()
        table = [
            [
                encounter.name,
                f"{clear_rates[encounter.name].clears} / {clear_rates[encounter.name].eligible_members}",
                f"{clear_rates[encounter.name].clear_rate * 100:.2f}%"
            ]
            for encounter in TRACKED_ENCOUNTERS
        ]
        data_str = tabulate(table,
                            headers=['Encounter', 'FC clears', 'FC clear rate'])

        super().__init__(
            ':white_check_mark:',
            f'Across Clear Rates: {date.today()}',
            None,
            data_str,
            None
        )
