from acrossfc.etl.update_fflogs_fc import UpdateFFLogsFC


def lambda_handler(event, context):
    # Prod
    # UpdateFFLogsFC(prod=True).run()

    # Test
    UpdateFFLogsFC().run()
    return "Completed successfully."
