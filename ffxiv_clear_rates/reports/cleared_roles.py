# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TRACKED_ENCOUNTERS, JOB_CATEGORIES
from .report import Report


def cleared_roles(database: Database) -> Report:
    cleared_jobs = database.get_cleared_jobs()

    table = []
    for encounter in TRACKED_ENCOUNTERS:
        cleared_members_by_role = {
            cat.name: set()
            for cat in JOB_CATEGORIES
        }
        for cleared_job in cleared_jobs[encounter.name]:
            # TODO: Dedupe by person
            cleared_members_by_role[cleared_job[1].main_category_id].add(cleared_job[0].fcid)
            if cleared_job[1].sub_category_id is not None:
                cleared_members_by_role[cleared_job[1].sub_category_id].add(cleared_job[0].fcid)

        table.append([encounter.name] + [len(cleared_members_by_role[cat.name]) for cat in JOB_CATEGORIES])

    data_str = tabulate(table, headers=[cat.name for cat in JOB_CATEGORIES], tablefmt="tsv")

    return Report(
        ':white_check_mark:',
        'Cleared Roles:',
        None,
        data_str,
        None
    )
