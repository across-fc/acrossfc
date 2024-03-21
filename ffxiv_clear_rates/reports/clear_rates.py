# stdlib
from typing import Dict
from datetime import date

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounterName, ClearRate, ACTIVE_TRACKED_ENCOUNTER_NAMES
from .report import Report


class ClearRates(Report):
    def __init__(self, database: Database):
        clear_rates: Dict[TrackedEncounterName, ClearRate] = database.get_clear_rates()

        table = []
        self.data_dict = {}
        for encounter_name in ACTIVE_TRACKED_ENCOUNTER_NAMES:
            cr = clear_rates[encounter_name]
            table.append(
                [
                    encounter_name,
                    f"{cr.clears} / {cr.eligible_members}",
                    f"{cr.clear_rate * 100:.2f}%",
                ]
            )
            self.data_dict[encounter_name] = {
                "clears": cr.clears,
                "total_eligible": cr.eligible_members,
                "clear_rate": cr.clear_rate,
            }

        data_str = tabulate(table, headers=["Encounter", "FC clears", "FC clear rate"])

        super().__init__(
            ":white_check_mark:",
            f"Across Clear Rates: {date.today()}",
            None,
            data_str,
            None,
        )

    def to_dict(self):
        return self.data_dict
