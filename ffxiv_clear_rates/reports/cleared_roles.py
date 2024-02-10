# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import JobCategory
from .report import Report


def cleared_roles(database: Database) -> Report:
    cleared_jobs = database.get_cleared_jobs()

    table = []
    for encounter in cleared_jobs:
        cleared_cat_counts = {
            cat: 0
            for cat in JobCategory
        }
        for cleared_job in cleared_jobs[encounter]:
            cleared_cat_counts[cleared_job[1].main_category] += 1
            if cleared_job[1].sub_category is not None:
                cleared_cat_counts[cleared_job[1].sub_category] += 1

        table.append([encounter.name] + [cleared_cat_counts[cat] for cat in JobCategory])

    data_str = tabulate(table, headers=[cat.name for cat in JobCategory], tablefmt="tsv")

    return Report(
        ':white_check_mark:',
        'Cleared Roles',
        None,
        data_str,
        None
    )
