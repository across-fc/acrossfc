# stdlib
import logging
from io import StringIO
from datetime import date
from typing import Optional

# Local
from ffxiv_clear_rates.database import Database
from .report import Report

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FCRoster(Report):
    def __init__(self, database: Database, gsheet_id: Optional[str] = None):
        self.gsheet_id = gsheet_id

        members = sorted([f"{member.name} ({member.fcid})" for member in database.get_fc_roster()])

        buffer = StringIO()

        for i, member in enumerate(members):
            if i > 0:
                buffer.write('\n')
            buffer.write(f"{i+1:>3}: {member}")

        super().__init__(
            ':ballot_box_with_check:',
            f'FC Roster: {date.today()}',
            None,
            buffer.getvalue(),
            None
        )

    def publish_to_gsheets(self) -> bool:
        if self.gsheet_id is None:
            LOG.info('No Google Sheet ID given. No report will be published to Google Drive.')
            return False

        # TODO: Implement
        return True
