# stdlib
from io import StringIO
from datetime import date
from typing import List, Dict
from collections import defaultdict

# 3rd-party
from tabulate import tabulate

# Local
from acrossfc.core.database import ClearDatabase
from acrossfc.core.model import Member, Job
from acrossfc.core.constants import JOBS
from .report_base import Report


class ClearedJobsByMember(Report):
    def __init__(
        self,
        database: ClearDatabase,
        encounter_names: List[str],
        jobs: List[Job],
        include_echo: bool = False
    ):
        cleared_jobs = database.get_cleared_jobs(include_echo=include_echo)

        buffer = StringIO()

        for i, encounter_name in enumerate(encounter_names):
            if i > 0:
                buffer.write("\n\n")

            # Manually do a group-by. itertools.groupby seems to be oddly random...
            member_cleared_jobs: Dict[Member, List[Job]] = defaultdict(list)
            for member_cleared_job in cleared_jobs[encounter_name]:
                if member_cleared_job[1] not in jobs:
                    continue
                member_cleared_jobs[member_cleared_job[0]].append(member_cleared_job[1])

            member_cleared_jobs = sorted(
                member_cleared_jobs.items(), key=lambda i: (-len(i[1]), i[0].name)
            )

            buffer.write(f"[{encounter_name}]")
            buffer.write("\n\n")
            table = []
            for i, item in enumerate(member_cleared_jobs):
                table.append(
                    [item[0].name, len(item[1]), ", ".join(job.tla for job in item[1])]
                )
            buffer.write(
                tabulate(table, headers=["Member", "Total", "Jobs"], tablefmt="simple")
            )
        if jobs != JOBS:
            title = (
                "Members who cleared on "
                + ", ".join(j.tla for j in jobs)
                + f" (as of {date.today()}):"
            )
        else:
            title = f"Cleared Jobs by Member (as of {date.today()}):"

        super().__init__(
            ":white_check_mark:",
            title,
            "Names displayed in alphabetical order",
            buffer.getvalue(),
            None,
        )
