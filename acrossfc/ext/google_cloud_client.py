# stdlib
import os

# 3rd-party
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes required to access Google Sheets API
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleCloudClient:
    def __init__(self, gc_creds_filename: str):
        # Authenticate with Google Sheets and Drive APIs
        creds = service_account.Credentials.from_service_account_file(
            gc_creds_filename, scopes=_SCOPES
        )
        self.GSHEETS = build("sheets", "v4", credentials=creds)
        self.GDRIVE = build("drive", "v3", credentials=creds)

    @property
    def sheets(self):
        return self.GSHEETS

    @property
    def drive(self):
        return self.GDRIVE


gc_creds_filename = os.environ.get('AX_GC_CREDS', '.gc_creds.json')
GC_CLIENT = GoogleCloudClient(gc_creds_filename=gc_creds_filename)
