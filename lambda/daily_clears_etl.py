from acrossfc.etl.clears_etl import ClearsETL


def lambda_handler(event, context):
    # Prod
    # ClearsETL(prod=True).run()

    # Test
    ClearsETL().run()
    return "Completed successfuly."
