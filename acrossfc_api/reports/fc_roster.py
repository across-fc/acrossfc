# stdlib
import logging
from io import StringIO
from datetime import date

# Local
from acrossfc_api.database import Database
from acrossfc_api.config import FC_CONFIG
from .report import Report
from .gapi import GAPI

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class FCRoster(Report):
    def __init__(self, database: Database):
        self.members = sorted(database.get_fc_roster(), key=lambda m: (m.rank, m.name))

        buffer = StringIO()

        for i, member in enumerate(self.members):
            if i > 0:
                buffer.write("\n")
            buffer.write(f"{i+1:>3}: {member.name} ({member.fcid})")

        super().__init__(
            ":ballot_box_with_check:",
            f"FC Roster: {date.today()}",
            None,
            buffer.getvalue(),
            None,
        )

    def publish_to_gsheets(self) -> bool:
        gsheet_id = FC_CONFIG.fc_roster_gsheets_id
        if gsheet_id is None:
            LOG.info(
                "No Google Sheet ID given. No report will be published to Google Drive."
            )
            return False

        # Add a new sheet to the spreadsheet
        request = GAPI.sheets.spreadsheets().batchUpdate(
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

        request = GAPI.sheets.spreadsheets().batchUpdate(
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
                                for member in self.members
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
                                "endRowIndex": len(self.members) + 1,
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
                                "endRowIndex": len(self.members) + 1,
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

        return True
