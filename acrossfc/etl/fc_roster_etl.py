# stdlib
import logging
from typing import List
from datetime import date

# Local
from acrossfc.core.model import Member
from acrossfc.core.config import FC_CONFIG
from acrossfc.ext.fflogs_client import FFLOGS_CLIENT
from acrossfc.ext.google_cloud_client import GC_CLIENT
from .etl_job_base import ETLJob

LOG = logging.getLogger(__name__)


class FCRosterETL(ETLJob):
    def run(self):
        LOG.debug('********** RUNNING FC ROSTER ETL')
        fc_roster: List[Member] = FFLOGS_CLIENT.get_fc_roster(
            guild_id=FC_CONFIG.fflogs_guild_id,
            guild_rank_filter=lambda rank: rank not in FC_CONFIG.exclude_guild_ranks,
        )

        gsheet_id = FC_CONFIG.fc_roster_gsheets_id
        if gsheet_id is None:
            LOG.info("No Google Sheet ID given. No report will be published to Google Drive.")

        # Add a new sheet to the spreadsheet
        request = GC_CLIENT.sheets.spreadsheets().batchUpdate(
            spreadsheetId=gsheet_id,
            body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "index": 0,
                                "title": f"{date.today()}",
                            }
                        },
                    },
                ]
            },
        )
        resp = request.execute()
        subsheet_id = resp["replies"][0]["addSheet"]["properties"]["sheetId"]

        # Insert FC roster into the new sheet
        request = GC_CLIENT.sheets.spreadsheets().batchUpdate(
            spreadsheetId=gsheet_id,
            body={
                "requests": [
                    {
                        "updateCells": {
                            "rows": [
                                {
                                    "values": [
                                        {
                                            "userEnteredValue": {"stringValue": "Name"},
                                        },
                                        {
                                            "userEnteredValue": {"stringValue": "Rank"},
                                        },
                                        {
                                            "userEnteredValue": {
                                                "stringValue": "FFLogs Character ID"
                                            },
                                        },
                                    ]
                                }
                            ]
                            + [
                                {
                                    "values": [
                                        {
                                            "userEnteredValue": {
                                                "stringValue": member.name
                                            },
                                        },
                                        {
                                            "userEnteredValue": {
                                                "numberValue": member.rank
                                            },
                                        },
                                        {
                                            "userEnteredValue": {
                                                "numberValue": member.fcid
                                            },
                                        },
                                    ]
                                }
                                for member in fc_roster
                            ],
                            "fields": "*",
                            "start": {
                                "sheetId": subsheet_id,
                                "rowIndex": 0,
                                "columnIndex": 0,
                            },
                        },
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": subsheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": len(fc_roster) + 1,
                                "startColumnIndex": 1,  # Second column
                                "endColumnIndex": 2,  # Up to second column
                            },
                            "cell": {
                                "userEnteredFormat": {"horizontalAlignment": "CENTER"}
                            },
                            "fields": "userEnteredFormat.horizontalAlignment",
                        }
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": subsheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": len(fc_roster) + 1,
                                "startColumnIndex": 2,  # Second column
                                "endColumnIndex": 3,  # Up to second column
                            },
                            "cell": {
                                "userEnteredFormat": {"horizontalAlignment": "RIGHT"}
                            },
                            "fields": "userEnteredFormat.horizontalAlignment",
                        }
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": subsheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 0,
                                "endColumnIndex": 3,
                            },
                            "cell": {
                                "userEnteredFormat": {"textFormat": {"bold": True}}
                            },
                            "fields": "userEnteredFormat.textFormat",
                        }
                    },
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": subsheet_id,
                                "gridProperties": {"frozenRowCount": 1},
                            },
                            "fields": "gridProperties.frozenRowCount",
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": subsheet_id,
                                "dimension": "COLUMNS",  # Dimension to adjust (ROWS or COLUMNS)
                                "startIndex": 0,  # Start index of the column
                                "endIndex": 1,  # End index of the column
                            },
                            "properties": {
                                "pixelSize": 200  # Width of the column in pixels
                            },
                            "fields": "pixelSize",  # Field to update
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": subsheet_id,
                                "dimension": "COLUMNS",  # Dimension to adjust (ROWS or COLUMNS)
                                "startIndex": 1,  # Start index of the column
                                "endIndex": 2,  # End index of the column
                            },
                            "properties": {
                                "pixelSize": 70  # Width of the column in pixels
                            },
                            "fields": "pixelSize",  # Field to update
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": subsheet_id,
                                "dimension": "COLUMNS",  # Dimension to adjust (ROWS or COLUMNS)
                                "startIndex": 2,  # Start index of the column
                                "endIndex": 3,  # End index of the column
                            },
                            "properties": {
                                "pixelSize": 160  # Width of the column in pixels
                            },
                            "fields": "pixelSize",  # Field to update
                        }
                    },
                ]
            },
        )
        request.execute()
        LOG.info(f"Successfully updated sheet https://docs.google.com/spreadsheets/d/{FC_CONFIG.fc_roster_gsheets_id}")
