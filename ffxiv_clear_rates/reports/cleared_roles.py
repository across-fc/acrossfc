# stdlib
from datetime import date

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import ACTIVE_TRACKED_ENCOUNTER_NAMES, JOB_CATEGORIES
from .report import Report


class ClearedRoles(Report):
    def __init__(self, database: Database):
        cleared_jobs = database.get_cleared_jobs()

        table = []
        for encounter_name in ACTIVE_TRACKED_ENCOUNTER_NAMES:
            cleared_members_by_role = {cat.name: set() for cat in JOB_CATEGORIES}
            for cleared_job in cleared_jobs[encounter_name]:
                # TODO: Dedupe by person
                cleared_members_by_role[cleared_job[1].main_category_id].add(
                    cleared_job[0].fcid
                )
                if cleared_job[1].sub_category_id is not None:
                    cleared_members_by_role[cleared_job[1].sub_category_id].add(
                        cleared_job[0].fcid
                    )

            table.append(
                [encounter_name]
                + [len(cleared_members_by_role[cat.name]) for cat in JOB_CATEGORIES]
            )

        data_str = tabulate(
            table, headers=[cat.name for cat in JOB_CATEGORIES], tablefmt="tsv"
        )

        super().__init__(
            ":white_check_mark:",
            f"Cleared Roles (as of {date.today()}):",
            None,
            data_str,
            None,
        )
