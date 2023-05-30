from connection import *
import config


class User(object):
    """Класс позволяет: участвовать в ивентах, свои успехи и успехи других, изменять настройки данных,
    предлагать что-то новое или жаловаться на некомпетентность организации."""

    def __int__(self):
        pass

    @staticmethod
    def authorization(user_name, user_group, user_phone, user_telegram, user_id,
                      user_scores='0.0', user_anonymity='FALSE', user_status='user', user_event='0'):
        """Функция позволяет авторизоваться в общую таблицу ивентов"""
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Атрибуты юзера
            values = ((user_name, user_group, user_phone, user_telegram, user_id,
                       user_scores, user_anonymity, user_status, user_event),)
            destruction_sheet_current_events = {'majorDimension': 'ROWS', 'values': values}

            # Перенос данных в таблицу выбранного ивента
            service.spreadsheets().values().append(spreadsheetId=config.sheet_vol_id,
                                                   range=config.range_name,
                                                   valueInputOption=config.raw_value_input_option,
                                                   body=destruction_sheet_current_events).execute()

        except HttpError as err:
            print(err)

    @staticmethod
    def check_presence(participate_sheet_id, user_id):
        """Проверка на наличие в таблице пользователя"""
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        cur_sheet = service.spreadsheets().values().get(spreadsheetId=participate_sheet_id,
                                                        range=config.range_raw).execute()
        if 'values' not in cur_sheet:
            return False
        value_sheet = cur_sheet['values']
        for value in value_sheet:
            if len(value) > 0 and value[4] == str(user_id):
                return True

    @staticmethod
    def participate_event(participate_sheet_id, user_id):
        """Метод позвозяет: отправлять данных в таблицу ивента"""
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                            range=config.range_raw).execute()['values']

            for index, cell in enumerate(vol_sheet):
                if len(cell) > 0 and cell[4] == user_id:
                    # Атрибуты юзера
                    values = ((cell[0], cell[1], cell[2], cell[3], cell[4], cell[5], cell[6]),)
                    destruction_sheet_current_events = {'majorDimension': 'ROWS', 'values': values}

                    # Перенос данных в таблицу выбранного ивента
                    service.spreadsheets().values().append(spreadsheetId=participate_sheet_id,
                                                           range=config.range_name,
                                                           valueInputOption=config.raw_value_input_option,
                                                           body=destruction_sheet_current_events).execute()

        except HttpError as err:
            print(err)

    @staticmethod
    def view_own_history(user_id):
        """Позволяет считать перечень событий в которых участвовал пользователь
         с таблицы "История участия в ивентах" """
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())
            vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                            range=config.range_raw).execute()['values']
            history = ""
            for index, cell in enumerate(vol_sheet):
                if len(cell) > 0 and cell[4] == user_id:
                    history += f"{cell[0]} - {cell[5]} рейтингових балов"
            return history
        except HttpError as err:
            print(err)

    @staticmethod
    def view_others_history():
        """Позволяет считать перечень событий в которых участвовали другие
         пользователи с таблицы "История участия в ивентах", если их
          свойство анонимности False"""
        try:
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Call the Sheets API
            result = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                         range=config.range_raw).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return
            history = ""
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                if len(row) > 0 and len(row[0]) > 0 and len(row[5]) > 0 and row[6] != "TRUE":
                    history += f"{row[0]} - {row[5]}\n"
            return history
        except HttpError as err:
            print(err)

    @staticmethod
    def change_anonymity(user_id, user_anonymity):
        """Изменяет свойство анонимности у пользователя в таблице "История участия в ивентах" """

        # Вызов Google Sheets API
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                        range=config.range_raw).execute()['values']
        for index, cell in enumerate(vol_sheet):
            if len(cell) > 0 and cell[4] == user_id:
                anonymity_value = ((f"{user_anonymity}",),)
                anonymity_range_body = {'majorDimension': 'ROWS', 'values': anonymity_value}

                # Изменение переменной цели в таблице:"Участники Волонтёрства".
                service.spreadsheets().values().update(spreadsheetId=config.sheet_vol_id,
                                                       range=f"G{index + 1}",
                                                       valueInputOption=config.raw_value_input_option,
                                                       body=anonymity_range_body).execute()

    @staticmethod
    def give_own_data(user_id):
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())
            vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                            range=config.range_raw).execute()['values']

            history = ""
            for index, cell in enumerate(vol_sheet):
                if len(cell) > 0 and cell[4] == user_id:
                    history += f"{cell[0]}\n{cell[1]}\n{cell[2]}\n{cell[3]}\n{cell[5]} балів\nУчасть у івентах: {cell[8]}"
            return history
        except HttpError as err:
            print(err)

    @staticmethod
    def change_setting(user_id, user_range, user_setting):
        """Изменяет свойство у пользователя в таблице "История участия в ивентах" """

        # Вызов Google Sheets API
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                        range=config.range_raw).execute()['values']
        for index, cell in enumerate(vol_sheet):
            if len(cell) > 0 and cell[4] == user_id:
                value = ((f"{user_setting}",),)
                range_body = {'majorDimension': 'ROWS', 'values': value}
                # Изменение переменной цели в таблице:"Участники Волонтёрства".
                service.spreadsheets().values().update(spreadsheetId=config.sheet_vol_id,
                                                       range=f"{user_range}{index + 1}",
                                                       valueInputOption=config.raw_value_input_option,
                                                       body=range_body).execute()

    def complain(self):
        """Отсылает текст модератору"""
        pass

    def give_advise(self):
        """Отсылает текст модератору"""
        pass
