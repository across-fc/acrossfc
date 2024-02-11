import sys
from ffxiv_clear_rates.main import run


def lambda_handler(event, context):
    sys.argv = [
        'main.py',
        'fc_roster',
        '-c', '/opt/python/.fcconfig',
        '-s', '/opt/python/.gc_creds.json',
        '-pg'
    ]
    run()
    return {
        'statusCode': 200,
        'body': 'Success'
    }
