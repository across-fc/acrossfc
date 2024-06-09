# stdlib
from io import StringIO
from typing import List

# Local
from acrossfc_api.core.database import Database
from .report import Report


class WhoClearedRecently(Report):
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

            encounter_clear_chart = database.get_clear_order(include_echo=include_echo)[encounter_name]

            buffer.write(f"[{encounter_name}]")
            buffer.write("\n\n")

            clear_date_str = encounter_clear_chart[-1][0].isoformat()
            clearees = ", ".join(member.name for member in encounter_clear_chart[-1][1])
            buffer.write(f"{clear_date_str}: {clearees}")

        super().__init__(
            ":white_check_mark:", "Who cleared recently:", None, buffer.getvalue(), None
        )
