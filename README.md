# ffxiv-clear-rates

Simple tool for tracking FFXIV clear rates.

This is a prototype for a future tool to be planned by my FC.

## Requirements:

* Python 3.12+
* Obtain an FFLogs API client ID and secret from the [FFLogs client management page](https://www.fflogs.com/api/clients/)

## Setting up FFLogs API credentials:

Create a folder named `.secrets`, and put two files in it named `client_id` and `client_secret` (no file extension).

The contents of the `client_id` file should be your FFLogs API client ID, and the contents of the `client_secret` file should be your FFLogs API client secret.

## Usage:

```
> pip install -r requirements.txt
> python main.py
```

The script will automatically load any FFLogs API client secrets stored in the `.secrets` folder.

**Help:**
```
> python main.py --help
usage: main.py [-h] [--secrets_folder SECRETS_FOLDER] [--guild_id GUILD_ID] [--verbose]

options:
  -h, --help            show this help message and exit
  --secrets_folder SECRETS_FOLDER, -s SECRETS_FOLDER
                        Path to the secrets folder.
  --guild_id GUILD_ID, -g GUILD_ID
                        FFLogs guild ID
  --verbose, -v         Turn on verbose logging
```

**Using a different secrets folder:**
```
> python main.py -s <path_to_secrets_folder>
```

**Checking clear rates for a different FC:**
```
> python main.py -g <fflogs_guild_id>
```
* Note that the tool will automatically filter out guild members with a rank higher than 6 (5 on the site) because that's how my FC works.

**Verbose mode**
```
> python main.py -v
```