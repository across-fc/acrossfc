# Local
from ffxiv_clear_rates.database import Database


def fc_roster(database: Database):
    members = sorted([f"{member.name} ({member.id})" for member in database.guild_members])

    print()
    print('FC roster:')
    print('-------------------------')
    for i, member in enumerate(members):
        print(f"{i+1:>3}: {member}")
