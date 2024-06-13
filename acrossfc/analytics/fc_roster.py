# stdlib
import logging
from io import StringIO
from datetime import date

# Local
from acrossfc.core.database import ClearDatabase
from .report_base import Report

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FCRoster(Report):
    def __init__(self, database: ClearDatabase):
        self.members = sorted(database.get_fc_roster(), key=lambda m: (m.rank, m.name))

        buffer = StringIO()

        for i, member in enumerate(self.members):
            if i > 0:
                buffer.write("\n")
            buffer.write(f"{i+1:>3}: {member.name} ({member.fcid})")

        super().__init__(
            ":ballot_box_with_check:",
            f"FC Roster: {date.today()}",
            None,
            buffer.getvalue(),
            None,
        )
