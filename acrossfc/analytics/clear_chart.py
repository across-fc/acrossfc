# stdlib
import logging
from datetime import date, timedelta
from typing import List

# 3rd-party
from tabulate import tabulate

# Local
from acrossfc.core.database import ClearDatabase
from .report_base import Report

LOG = logging.getLogger(__name__)


class ClearChart(Report):
    def __init__(
        self,
        database: ClearDatabase,
        encounter_names: List[str],
        include_echo: bool = False
    ):
        clear_order = database.get_clear_order(include_echo=include_echo)

        # Change member list to number of members
        for encounter_name in encounter_names:
            number_of_data_points = len(clear_order[encounter_name])
            cumulative_cleared = 0
            for i in range(number_of_data_points):
                datapoint = clear_order[encounter_name][i]
                cumulative_cleared += len(datapoint[1])
                clear_order[encounter_name][i] = (datapoint[0], cumulative_cleared)

        print({
            k: len(clear_order[k])
            for k in clear_order
        })
        print(list(encounter_names))

        # Figure out date boundaries
        earliest_date = sorted(
            [clear_order[encounter_name][0][0] for encounter_name in encounter_names]
        )[0]
        latest_date = sorted(
            [clear_order[encounter_name][-1][0] for encounter_name in encounter_names]
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
                        for datapoint in reversed(clear_order[encounter_name])
                        if datapoint[0] <= current_date
                    ),
                    0,
                )
                for encounter_name in encounter_names
            ]
            table.append([current_date.isoformat()] + clears)
            current_date += timedelta(days=1)

        data_str = tabulate(
            table, headers=[encounter_name for encounter_name in encounter_names], tablefmt="tsv"
        )

        super().__init__(
            None, f"Across Clear Chart: {date.today()}", None, data_str, None
        )
