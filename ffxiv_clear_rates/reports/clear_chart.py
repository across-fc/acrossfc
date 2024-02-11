# stdlib
import logging
from datetime import date, timedelta

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TRACKED_ENCOUNTERS
from .report import Report

LOG = logging.getLogger(__name__)


def clear_chart(database: Database) -> Report:
    clear_order = database.get_clear_order()

    # Change member list to number of members
    for encounter_name in clear_order:
        number_of_data_points = len(clear_order[encounter_name])
        cumulative_cleared = 0
        for i in range(number_of_data_points):
            datapoint = clear_order[encounter_name][i]
            cumulative_cleared += len(datapoint[1])
            clear_order[encounter_name][i] = (
                datapoint[0], cumulative_cleared
            )

    earliest_date = sorted([
        clear_order[encounter][0][0]
        for encounter in clear_order
    ])[0]
    latest_date = sorted([
        clear_order[encounter][-1][0]
        for encounter in clear_order
    ])[-1]

    table = []
    current_date = earliest_date
    while current_date <= latest_date:
        LOG.debug(f'Processing {current_date.isoformat()}...')
        clears = [
            next(
                (
                    datapoint[1]
                    for datapoint in reversed(clear_order[encounter.name])
                    if datapoint[0] <= current_date
                ),
                0
            )
            for encounter in TRACKED_ENCOUNTERS
        ]
        table.append([current_date.isoformat()] + clears)
        current_date += timedelta(days=1)

    data_str = tabulate(table,
                        headers=[encounter.name for encounter in TRACKED_ENCOUNTERS],
                        tablefmt="tsv")

    return Report(
        None,
        f'Across Clear Chart: {date.today()}',
        None,
        data_str,
        None
    )
