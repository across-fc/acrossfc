from acrossfc.etl.fc_clears_etl import fc_clears_etl


def lambda_handler(event, context):
    fc_clears_etl()
    return "Completed successfuly."
