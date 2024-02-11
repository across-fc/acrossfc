# stdlib
import tempfile
import logging
import shutil
from typing import List, Dict, Set, Tuple
from datetime import date
from collections import defaultdict

# 3rd-party
from peewee import SqliteDatabase, fn, JOIN, prefetch

# Local
from ffxiv_clear_rates.model import (
    Member,
    TrackedEncounter,
    TrackedEncounterName,
    JobCategory,
    Job,
    Clear,
    ClearRate,
    ALL_MODELS,
    TRACKED_ENCOUNTERS,
    JOB_CATEGORIES,
    JOBS
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Database:
    def __init__(self, db_filename: str):
        self.db_filename = db_filename
        self._db = SqliteDatabase(self.db_filename)

    def save(self, filename: str):
        shutil.copy(self.db_filename, filename)

    @staticmethod
    def from_fflogs(members: List[Member], clears: List[Clear]) -> 'Database':
        db_filename = tempfile.NamedTemporaryFile().name
        db = Database(db_filename)

        # Setup database
        with db._db.bind_ctx(ALL_MODELS):
            db._db.create_tables(ALL_MODELS)
            TrackedEncounter.bulk_create(TRACKED_ENCOUNTERS)
            JobCategory.bulk_create(JOB_CATEGORIES)
            Job.bulk_create(JOBS)
            Member.bulk_create(members)
            Clear.bulk_create(clears, batch_size=50)

        return db

    def get_fc_roster(self) -> List[Member]:
        with self._db.bind_ctx(ALL_MODELS):
            return Member.select().order_by(Member.rank, Member.name)

    def get_clear_rates(self) -> Dict[TrackedEncounterName, ClearRate]:
        with self._db.bind_ctx(ALL_MODELS):
            eligible_members = Member.select().count()
            query = (TrackedEncounter
                     .select(TrackedEncounter, fn.Count(fn.Distinct(Clear.member)).alias('count'))
                     .join(Clear)
                     .group_by(TrackedEncounter))

        ret = {
            row.name: ClearRate(row.count, eligible_members)
            for row in query
        }

        return ret

    def get_cleared_members_by_encounter(self, encounter: TrackedEncounter) -> Set[Member]:
        with self._db.bind_ctx(ALL_MODELS):
            query = (Member
                     .select()
                     .join(Clear)
                     .where(Clear.encounter == encounter.name)
                     .distinct())

        return query

    def get_uncleared_members_by_encounter(self, encounter: TrackedEncounter) -> Set[Member]:
        with self._db.bind_ctx(ALL_MODELS):
            members_with_clear = (Member
                                  .select()
                                  .join(Clear)
                                  .where(Clear.encounter == encounter.name)
                                  .distinct())

            members_without_clear = (Member
                                     .select()
                                     .join(members_with_clear,
                                           JOIN.LEFT_OUTER,
                                           on=(Member.fcid == members_with_clear.c.fcid))
                                     .where(members_with_clear.c.fcid >> None))

        return set(members_without_clear)

    def get_clear_order(self) -> Dict[TrackedEncounterName, List[Tuple[date, Set[Member]]]]:
        # {
        #     <encounter_name>: [
        #         (<date>, <cleared_members_set>),
        #         (<date>, <cleared_members_set>),
        #         (<date>, <cleared_members_set>),
        #         ...
        #     ]
        # }
        with self._db.bind_ctx(ALL_MODELS):
            # Get index of members
            clear_chart = defaultdict(list)
            query = (Clear
                     .select(Clear.encounter,
                             Clear.member,
                             fn.MIN(fn.DATE(Clear.start_time)).alias('first_clear_date'))
                     .group_by(Clear.encounter, Clear.member)
                     .order_by(Clear.encounter, fn.MIN(fn.DATE(Clear.start_time)))
                     .alias('subquery'))

            for row in query:
                clear_date = date.fromisoformat(row.first_clear_date)
                encounter_clear_chart = clear_chart[row.encounter.name]
                if len(encounter_clear_chart) == 0:
                    encounter_clear_chart.append(
                        (clear_date, {row.member})
                    )
                else:
                    last_clear_date = encounter_clear_chart[-1][0]
                    if clear_date > last_clear_date:
                        encounter_clear_chart.append(
                            (clear_date, {row.member})
                        )
                    else:
                        encounter_clear_chart[-1][1].add(row.member)

        return clear_chart

    def get_cleared_jobs(self) -> Dict[TrackedEncounterName, Set[Tuple[Member, Job]]]:
        encounter_cleared_jobs = defaultdict(set)

        with self._db.bind_ctx(ALL_MODELS):
            query = (Clear
                     .select(Clear.encounter, Clear.member, Clear.job)
                     .group_by(Clear.encounter, Clear.member, Clear.job)
                     .order_by(Clear.encounter, Clear.member, Clear.job))

            for row in query:
                new_datapoint = (row.member, row.job)
                encounter_cleared_jobs[row.encounter.name].add(new_datapoint)  # Set will automatically de-dupe

        return encounter_cleared_jobs
