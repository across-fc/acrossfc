from acrossfc.etl.fc_roster_etl import FCRosterETL


def lambda_handler(event, context):
    FCRosterETL(prod=True).run()
    return "Completed successfuly."
