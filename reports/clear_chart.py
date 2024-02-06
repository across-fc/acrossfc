# stdlib
import logging
from datetime import timedelta

# 3rd-party
from tabulate import tabulate

# Local
from database import Database

LOG = logging.getLogger(__name__)


def clear_chart(database: Database):
    clear_chart = database.get_clear_chart()

    # Change member list to number of members
    for encounter in clear_chart:
        number_of_data_points = len(clear_chart[encounter])
        for i in range(number_of_data_points):
            datapoint = clear_chart[encounter][i]
            clear_chart[encounter][i] = (
                datapoint[0], len(datapoint[1])
            )

    earliest_date = sorted([
        clear_chart[encounter][0][0]
        for encounter in clear_chart
    ])[0]
    latest_date = sorted([
        clear_chart[encounter][-1][0]
        for encounter in clear_chart
    ])[-1]

    table = []
    current_date = earliest_date
    while current_date <= latest_date:
        LOG.debug(f'Processing {current_date.isoformat()}...')
        clears = [
            next(
                (
                    datapoint[1]
                    for datapoint in reversed(clear_chart[encounter])
                    if datapoint[0] <= current_date
                ),
                0
            )
            for encounter in clear_chart
        ]
        table.append([current_date.isoformat()] + clears)
        current_date += timedelta(days=1)

    print(tabulate(table,
                   headers=[encounter.name for encounter in clear_chart],
                   tablefmt="tsv"))