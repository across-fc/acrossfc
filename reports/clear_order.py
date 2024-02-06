# 3rd-party
from tabulate import tabulate

# Local
from database import Database


def clear_order(database: Database):
    clear_chart = database.get_clear_chart()

    for encounter in clear_chart:
        print()
        print(encounter.name)
        print('-----------------------')
        table = []
        current_clearees = set()
        for i, datapoint in enumerate(clear_chart[encounter]):
            table.append([
                i+1,
                datapoint[0],
                ', '.join([member.name for member in (datapoint[1] ^ current_clearees)])
            ])
            current_clearees = datapoint[1]
        print(tabulate(table, tablefmt="tsv"))
