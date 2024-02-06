from database import Database
from model import TrackedEncounter


def ppl_without_clear(database: Database, encounter: TrackedEncounter):
    uncleared_members = database.get_uncleared_members_by_encounter(encounter)
    sorted_names = sorted([
        f"{member.name} ({member.id})"
        for member in uncleared_members
    ])

    print()
    print(f'People who have not cleared {encounter.name}')
    print('-------------------------------------------------')
    for i, name in enumerate(sorted_names):
        print(f"{i+1:>2}: {name}")
