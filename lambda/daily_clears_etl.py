from acrossfc.etl.clears_etl import ClearsETL


def lambda_handler(event, context):
    ClearsETL(prod=True).run()
    return "Completed successfuly."
