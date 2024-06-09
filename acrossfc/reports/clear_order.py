# stdlib
from io import StringIO
from typing import List
from datetime import date

# 3rd-party
from tabulate import tabulate

# Local
from acrossfc.core.database import Database
from .report import Report


class ClearOrder(Report):
    def __init__(
        self,
        database: Database,
        encounter_names: List[str],
        include_echo: bool = False
    ):
        clear_order = database.get_clear_order(include_echo=include_echo)

        buffer = StringIO()
        for i, encounter_name in enumerate(encounter_names):
            if i > 0:
                buffer.write("\n\n")

            buffer.write(f"[{encounter_name}]")
            buffer.write("\n\n")
            table = []
            for i, datapoint in enumerate(clear_order[encounter_name]):
                table.append(
                    [
                        f"{i+1} ",
                        datapoint[0],
                        ", ".join(sorted([member.name for member in datapoint[1]])),
                    ]
                )
            buffer.write(
                tabulate(
                    table,
                    headers=["Order", "Clear Date", "Member(s)"],
                    tablefmt="simple",
                )
            )

        super().__init__(
            ":first_place:",
            f"Clear Order (as of {date.today()}):",
            None,
            buffer.getvalue(),
            None,
        )
