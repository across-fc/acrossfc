import sys
from acrossfc.api.main import run


def lambda_handler(event, context):
    sys.argv = [
        'main.py',
        'update_fflogs'
    ]
    run()

    return {
        'statusCode': 200,
        'body': 'Success'
    }
