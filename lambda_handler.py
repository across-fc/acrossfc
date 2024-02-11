import sys
from ffxiv_clear_rates.main import run


def publish_clear_rates(event, context):
    sys.argv = ['main.py', 'clear_rates', '-p']
    run()
    return True


def update_fflogs(event, context):
    sys.argv = ['main.py', 'update_fflogs']
    run()
    return True
