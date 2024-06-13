from acrossfc.etl.fc_roster_etl import FCRosterETL


def lambda_handler(event, context):
    # Prod
    # FCRosterETL(prod=True).run()

    # Test
    FCRosterETL().run()
    return "Completed successfuly."
