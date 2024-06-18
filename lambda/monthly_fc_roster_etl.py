from acrossfc.etl.fc_roster_etl import fc_roster_etl


def lambda_handler(event, context):
    fc_roster_etl()
    return "Completed successfuly."
