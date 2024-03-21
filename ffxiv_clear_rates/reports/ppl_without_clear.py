# stdlib
from io import StringIO
from typing import List
from datetime import date

# Local
from ffxiv_clear_rates.database import Database
from .report import Report


class PeopleWithoutClear(Report):
    def __init__(
        self,
        database: Database,
        encounter_names: List[str],
        include_echo: bool = False
    ):
        buffer = StringIO()

        for i, encounter_name in enumerate(encounter_names):
            if i > 0:
                buffer.write("\n\n")

            uncleared_members = database.get_uncleared_members_by_encounter(encounter_name, include_echo=include_echo)
            sorted_names = sorted([f"{member.name}" for member in uncleared_members])

            buffer.write(f"{encounter_name} ({len(sorted_names)})")
            buffer.write("\n-------------------------------------------------\n")
            for i, name in enumerate(sorted_names):
                if i > 0:
                    buffer.write("\n")
                buffer.write(f"{i+1:>2}: {name}")

        super().__init__(
            ":no_entry_sign:",
            f"People who have NOT cleared (as of {date.today()}):",
            "Names displayed in alphabetical order",
            buffer.getvalue(),
            None,
        )
