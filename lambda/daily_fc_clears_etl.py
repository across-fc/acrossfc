from acrossfc.etl.fc_clears_etl import FCClearsETL


def lambda_handler(event, context):
    FCClearsETL(prod=True).run()
    return "Completed successfuly."
