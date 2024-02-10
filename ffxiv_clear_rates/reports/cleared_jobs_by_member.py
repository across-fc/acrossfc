# stdlib
from io import StringIO
from typing import List, Dict
from collections import defaultdict

# Local
from ffxiv_clear_rates.database import Database
from ffxiv_clear_rates.model import GuildMember, Job, TrackedEncounter
from .report import Report


def cleared_jobs_by_member(database: Database, encounters: List[TrackedEncounter]) -> Report:
    cleared_jobs = database.get_cleared_jobs()

    buffer = StringIO()

    for i, encounter in enumerate(encounters):
        if i > 0:
            buffer.write('\n\n')

        # Manually do a group-by. itertools.groupby seems to be oddly random...
        member_cleared_jobs: Dict[GuildMember, List[Job]] = defaultdict(list)
        for member_cleared_job in cleared_jobs[encounter]:
            member_cleared_jobs[member_cleared_job[0]].append(member_cleared_job[1])
        member_cleared_jobs = sorted(member_cleared_jobs.items(), key=lambda i: len(i[1]), reverse=True)

        buffer.write(encounter.name)
        buffer.write('\n-------------------------\n')
        for i, item in enumerate(member_cleared_jobs):
            if i > 0:
                buffer.write('\n')
            buffer.write(f'{i:>2}: {item[0].name} ({len(item[1])}: {", ".join(job.acronym for job in item[1])})')

    return Report(
        ':white_check_mark:',
        'Cleared Jobs by Member:',
        None,
        buffer.getvalue(),
        None
    )
