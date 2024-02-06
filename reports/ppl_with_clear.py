from database import Database
from model import TrackedEncounter


def ppl_with_clear(database: Database, encounter: TrackedEncounter):
    cleared_members = database.get_cleared_members_by_encounter(encounter)
    sorted_names = sorted([
        f"{member.name} ({member.id})"
        for member in cleared_members
    ])

    print()
    print(f'People who have cleared {encounter.name}:')
    print('-------------------------------------------------')
    for i, name in enumerate(sorted_names):
        print(f"{i+1:>2}: {name}")
