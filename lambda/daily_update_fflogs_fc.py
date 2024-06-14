from acrossfc.etl.update_fflogs_fc import UpdateFFLogsFC


def lambda_handler(event, context):
    UpdateFFLogsFC(prod=True).run()
    return "Completed successfully."
