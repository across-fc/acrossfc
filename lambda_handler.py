import sys
from ffxiv_clear_rates.main import run


def handler(event, context):
    sys.argv = ['main.py', 'clear_rates', '-p']
    run()
