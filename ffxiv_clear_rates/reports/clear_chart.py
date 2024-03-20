# stdlib
import logging
from datetime import date, timedelta
from typing import List

# 3rd-party
from tabulate import tabulate

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import TrackedEncounter
from .report import Report

LOG = logging.getLogger(__name__)


class ClearChart(Report):
    def __init__(self, database: Database, encounters: List[TrackedEncounter]):
        clear_order = database.get_clear_order()

        # Change member list to number of members
        for encounter in encounters:
            number_of_data_points = len(clear_order[encounter.name])
            cumulative_cleared = 0
            for i in range(number_of_data_points):
                datapoint = clear_order[encounter.name][i]
                cumulative_cleared += len(datapoint[1])
                clear_order[encounter.name][i] = (datapoint[0], cumulative_cleared)

        # Figure out date boundaries
        earliest_date = sorted(
            [clear_order[encounter.name][0][0] for encounter in encounters]
        )[0]
        latest_date = sorted(
            [clear_order[encounter.name][-1][0] for encounter in encounters]
        )[-1]

        # Construct data table
        table = []
        current_date = earliest_date - timedelta(days=2)
        while current_date <= latest_date:
            LOG.debug(f"Processing {current_date.isoformat()}...")
            clears = [
                next(
                    (
                        datapoint[1]
                        for datapoint in reversed(clear_order[encounter.name])
                        if datapoint[0] <= current_date
                    ),
                    0,
                )
                for encounter in encounters
            ]
            table.append([current_date.isoformat()] + clears)
            current_date += timedelta(days=1)

        data_str = tabulate(
            table, headers=[encounter.name for encounter in encounters], tablefmt="tsv"
        )

        super().__init__(
            None, f"Across Clear Chart: {date.today()}", None, data_str, None
        )
