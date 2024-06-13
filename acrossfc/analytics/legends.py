# stdlib
from io import StringIO
from collections import defaultdict
from datetime import date

# 3rd-party
from tabulate import tabulate

# Local
from acrossfc.core.database import ClearDatabase
from acrossfc.core.model import ULTIMATE_NAMES
from .report import Report


class Legends(Report):
    def __init__(
        self,
        database: ClearDatabase,
    ):
        buffer = StringIO()
        member_to_cleared_ult = defaultdict(list)

        num_members = len(database.get_fc_roster())

        for i, encounter_name in enumerate(ULTIMATE_NAMES):
            cleared_members = database.get_cleared_members_by_encounter(encounter_name)
            for member in cleared_members:
                member_to_cleared_ult[member.name].append(encounter_name)

        sorted_names = sorted([f"{member_name}" for member_name in member_to_cleared_ult])
        for i in range(5):
            table = []
            for name in sorted_names:
                if len(member_to_cleared_ult[name]) == (i+1):
                    table.append(
                        [name, ", ".join(member_to_cleared_ult[name])]
                    )

            num_legends = len(table)
            fc_percentage = float(num_legends) / num_members

            if i > 0:
                buffer.write('\n\n')
            buffer.write(f"{i+1}x Legends: {len(table)} ({fc_percentage * 100:.2f}%)")
            buffer.write("\n-------------------------------------------------\n")
            buffer.write(
                tabulate(table, tablefmt="plain")
            )

        super().__init__(
            ":white_check_mark:",
            f"Legends (as of {date.today()}):",
            "Names displayed in alphabetical order",
            buffer.getvalue(),
            None,
        )
