# stdlib
from io import StringIO
from datetime import date

# Local
from ffxiv_clear_rates.database import Database
from .report import Report


def fc_roster(database: Database) -> Report:
    members = sorted([f"{member.name} ({member.id})" for member in database.guild_members])

    buffer = StringIO()

    for i, member in enumerate(members):
        if i > 0:
            buffer.write('\n')
        buffer.write(f"{i+1:>3}: {member}")

    return Report(
        ':ballot_box_with_check:',
        f'FC Roster: {date.today()}',
        None,
        buffer.getvalue(),
        None
    )
