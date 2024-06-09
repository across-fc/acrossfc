# acrossfc-api

Across FC Automation and Backend API

## Requirements:

* Python 3.12+
* Obtain an FFLogs API client ID and secret from the [FFLogs client management page](https://www.fflogs.com/api/clients/)

## Setup

Create a file named `.fcconfig` with the following contents, replacing all `<...>` segments with the appropriate values:

```ini
[DEFAULT]
fflogs_client_id = <client_id>
fflogs_client_secret = <client_secret>
fflogs_guild_id = 75624
exclude_guild_ranks = 5

# Optional: Discord webhook URL for posting results
discord_webhook_url = <webhook_url>

# Optional: Google Sheets ID for tracking the FC roster.
# Make sure the Google service account has write access to this document.
fc_roster_gsheets_id = <gsheets_id>
```

Put this file in the repository root.

**Optional:** Create a file named `.gc_creds.json` and put the Google service account credentials in it.

## Usage:

Install the project:

```
pip install -e .
```

This will install the `fcr` (read: `ffxiv_clear_rates`) command in your environment, which you can use to get clear rates and other types of clear-related data for your FC.

To install development / testing dependencies, use:

```
pip install -e ".[dev]"
```

### Get clear rates:

```
fcr clear_rates
```

Sample output:
```
Encounter    FC clears    FC clear rate
-----------  -----------  ---------------
P9S          68 / 77      88.31%
P10S         64 / 77      83.12%
P11S         61 / 77      79.22%
P12S_P1      44 / 77      57.14%
P12S         37 / 77      48.05%
UWU          29 / 77      37.66%
UCOB         22 / 77      28.57%
TEA          31 / 77      40.26%
DSR          21 / 77      27.27%
TOP          14 / 77      18.18%
```

### Publishing reports to Discord

If you have a Discord webhook URL configured in `.fcconfig` (see above), you can use the `-p` argument to automatically publish the report to your webhook:

```
fcr clear_rates -p
```

## Help:

```
fcr -h
```

This prints information on other available commands:
```
usage: fcr [-h]
           {clear_rates,fc_roster,clear_chart,clear_order,cleared_roles,cleared_jobs_by_member,who_cleared_recently,update_fflogs,ppl_without_clear,ppl_with_clear}
           ...

positional arguments:
  {clear_rates,fc_roster,clear_chart,clear_order,cleared_roles,cleared_jobs_by_member,who_cleared_recently,update_fflogs,ppl_without_clear,ppl_with_clear}
    clear_rates         Prints the FC clear rates.
    fc_roster           Prints the FC roster.
    clear_chart         Prints a chart of clears over time based on the current roster.
    clear_order         Prints the order of clears based on the current roster.
    cleared_roles       Prints the cleared roles based on the current roster.
    cleared_jobs_by_member
                        Prints the cleared jobs for each member.
    who_cleared_recently
                        Prints who cleared a certain encounter recently
    update_fflogs       Updates the FFLogs FC roster
    ppl_without_clear   Prints the list of people without a clear of a certain fight.
    ppl_with_clear      Prints the list of people with a clear of a certain fight.

options:
  -h, --help            show this help message and exit
```