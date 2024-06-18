from acrossfc.etl.update_fflogs_fc import update_fflogs_fc


def lambda_handler(event, context):
    update_fflogs_fc()
    return "Completed successfully."
