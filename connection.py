from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class Connection(object):
    """Класс включает в себя: определения области работы API, подключение к google sheets API
    Создания токена подключения, если его нет по файлу credentials.json
    (содержит реквизиты для входа)"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __int__(self, spreadsheet_id, range_name):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name

    @classmethod
    def get_connection(cls):
        """Подключение к google sheets"""
        credentials = None
        # В файле token.json хранятся токены доступа и обновления пользователя,
        # и он создается автоматически, когда поток авторизации завершается в первый раз.
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json', cls.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', cls.SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())
        return credentials

    @staticmethod
    def get_last_row(spreadsheet_id, range_name):
        """Нахождение последней строки"""
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        # Call the Sheets API
        response = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range=range_name).execute()
        last_row = 1
        last_row += len(response['values']) - 1
        print(last_row)
