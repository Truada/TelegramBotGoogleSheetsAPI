from user import *
import config
from time import sleep


class Admin(object):
    """Класс позволяет создавать, редактировать, отменять, потверждать мероприятия.
    Смотреть рейтинг и анти-рейтинг участников. Составлять отчёты по шаблонам. Получать данные из таблицы"""

    @staticmethod
    def get_source_data_sheet(sheet_vol_id, data_range):
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())
            # Запись в переменные значений таблицы "Участники Волонтёрства" и изъятие ID users.
            cur_sheet = service.spreadsheets().values().get(spreadsheetId=sheet_vol_id,
                                                            range=data_range).execute()
            list_none = list()
            if cur_sheet.get('values') is None:
                return list_none
            return list_none
        except HttpError as err:
            print(err)

    @staticmethod
    def get_present(sheet_vol_id):
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())
            # Запись в переменные значений таблицы "Участники Волонтёрства" и изъятие ID users.
            cur_sheet = service.spreadsheets().values().get(spreadsheetId=sheet_vol_id,
                                                            range=config.range_raw).execute()
            if cur_sheet.get('values') is None:
                return False
            else:
                return True
        except HttpError as err:
            print(err)

    @staticmethod
    def get_value_data_sheet(sheet_vol_id, data_range):
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())
            # Запись в переменные значений таблицы "Участники Волонтёрства" и изъятие ID users.
            cur_sheet = service.spreadsheets().values().get(spreadsheetId=sheet_vol_id,
                                                            range=data_range).execute()
            list_values = []
            if cur_sheet['values'] is None:
                return list_values
            for elem in cur_sheet['values']:
                if len(elem) > 0:
                    list_values.append(elem[0])

            return list_values

        except HttpError as err:
            print(err)

    @staticmethod
    def add_event(name_new_sheet, date_new_sheet, time_new_sheet, venue_new_sheet, type_event_new_sheet,
                  score_new_sheet):
        """Метод позволяет создавать таблицу НОВОГО ивента и добавлять её в ОБЩУЮ текущих ивентов"""
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Создаём новую таблицу ивента c кастомными настройками.
            new_sheet_body = {'properties': {'title': f"{name_new_sheet}"}}
            result = service.spreadsheets().create(body=new_sheet_body).execute()

            # Добавляем значени в id_new_sheet
            id_new_sheet = result['spreadsheetId']

            # Формируем значение запроса и его тело для добавления разметки и данных о новой таблице
            common_values = (
                (name_new_sheet, date_new_sheet, time_new_sheet, venue_new_sheet,
                 type_event_new_sheet, score_new_sheet, id_new_sheet),
            )

            body_sheet_current_events = {
                'majorDimension': 'ROWS',
                'values': common_values
            }
            markup_values = (
                ("ПІБ", "Група", "Номер телефона", "Telegram",
                 "Telegram", "ID", "Бали", "Анонимність",
                 "Юзер/Админ", "Участь у івентах"),
            )

            body_markup = {
                'majorDimension': 'ROWS',
                'values': markup_values
            }
            # Добавляем в новую таблицу разметку:
            service.spreadsheets().values().append(spreadsheetId=id_new_sheet,
                                                   range=config.range_raw,
                                                   valueInputOption=config.raw_value_input_option,
                                                   body=body_markup).execute()

            # Добавляем её в общую таблицу текущих ивентов
            service.spreadsheets().values().append(spreadsheetId=config.sheet_current_events_id,
                                                   range=config.range_raw,
                                                   valueInputOption=config.raw_value_input_option,
                                                   body=body_sheet_current_events).execute()

        except HttpError as err:
            print(err)

    @staticmethod
    def cancel_event(destruction_spreadsheet_id):
        """Метод позволяет удалять ивент из таблицы "Текущие ивенты" """

        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Запись в переменную всех значений таблицы в заданном диапазоне.
            result = service.spreadsheets().values().get(spreadsheetId=config.sheet_current_events_id,
                                                         range=config.range_raw).execute()

            # Поиск искомого события и удаление искомого события
            for index, cell in enumerate(result['values']):
                if len(cell) >= 7 and cell[6] == destruction_spreadsheet_id:
                    # Удаление значений из таблицы "Текущие значения"
                    service.spreadsheets().values().clear(spreadsheetId=config.sheet_current_events_id,
                                                          range=f"A{index + 1}:{index + 1}").execute()

        except HttpError as err:
            print(err)

    @staticmethod
    def confirm_event(destruction_spreadsheet_id):
        """Метод позволяет потверждать мероприятие: добавление в таблицу прошедших ивентов,
         добавление балов участникам сектора, удаление его из общей таблицы текущих ивентов"""
        try:
            # Вызов Google Sheets API
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Запись в переменные значений таблиц: "Ивент, который прошёл", "Текущие Инветы", "Участники Волонтёрства".
            destrution_sheet_id = service.spreadsheets().values().get(spreadsheetId=destruction_spreadsheet_id,
                                                                      range=config.range_user_id).execute()

            cur_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_current_events_id,
                                                            range=config.range_raw).execute()

            volunter_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                                 range=config.range_raw).execute()
            if destrution_sheet_id.get('values') is None or volunter_sheet.get('values') is None:
                return False

            destr_sheet_id = destrution_sheet_id['values']
            vol_sheet = volunter_sheet['values']
            # Костыль для нормального списка айди
            list_id = []
            for index, value in enumerate(destr_sheet_id):
                if len(value) > 0:
                    list_id.insert(index, value[0])

            # Поиск искомого события и удаление искомого события
            for index, cell in enumerate(cur_sheet['values']):
                if len(cell) >= 7 and cell[6] == destruction_spreadsheet_id:
                    # Атрибуты для переноса потверждённого ивента в таблицу "Прошедшие мероприятия"
                    values = ((cell[0], cell[1], cell[2], cell[3], cell[4], cell[5], cell[6]),)
                    destruction_sheet_current_events = {'majorDimension': 'ROWS', 'values': values}
                    score_coef = float(cell[5].replace(',', '.'))

                    # Начисление балов участникам и добавление одного пункта к атрибуту "Участие в ивентах"
                    for number, vol in enumerate(vol_sheet):
                        if len(vol) > 0 and vol[4] in list_id:
                            score_value = ((str(float(vol[5].replace(',', '.')) + score_coef),),)
                            if float(vol[5].replace(',', '.')) >= 5:
                                score_value = (("5.0",),)
                            participation_value = ((str(int(vol[8]) + 1),),)
                            score_range_body = {'majorDimension': 'ROWS', 'values': score_value}
                            participation_range_body = {'majorDimension': 'ROWS', 'values': participation_value}
                            sleep(0.05)
                            service.spreadsheets().values().update(spreadsheetId=config.sheet_vol_id,
                                                                   range=f"F{number + 1}",
                                                                   valueInputOption=config.raw_value_input_option,
                                                                   body=score_range_body).execute()
                            sleep(0.05)
                            service.spreadsheets().values().update(spreadsheetId=config.sheet_vol_id,
                                                                   range=f"I{number + 1}",
                                                                   valueInputOption=config.raw_value_input_option,
                                                                   body=participation_range_body).execute()

                    # Перенос потверждённого ивента в таблицу "Прошедшие мероприятия"
                    service.spreadsheets().values().append(spreadsheetId=config.sheet_past_events_id,
                                                           range=config.range_name,
                                                           valueInputOption=config.raw_value_input_option,
                                                           body=destruction_sheet_current_events).execute()

                    # Удаление значений из таблицы "Текущие значения"
                    service.spreadsheets().values().clear(spreadsheetId=config.sheet_current_events_id,
                                                          range=f"A{index + 1}:{index + 1}").execute()
                    break

        except HttpError as err:
            print(err)

    @staticmethod
    def get_scores():
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
                if len(row[0]) > 0 and len(row[5]) > 0 and row[6] != "TRUE":
                    history += f"{row[0]} - {row[5]}\n"
            return history

        except HttpError as err:
            print(err)

    @staticmethod
    def get_name_and_id(sheet_id):
        try:
            service = build('sheets', 'v4', credentials=Connection().get_connection())

            # Call the Sheets API
            result = service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                         range=config.range_raw).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return False

            history = ""
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                if len(row) > 0 and len(row[5]) > 0 and row[6] != "TRUE":
                    history += f"{row[0]} - {row[4]}\n"
            return history

        except HttpError as err:
            print(err)

    @staticmethod
    def delete_users(sheet_id, list_delete):
        service = build('sheets', 'v4', credentials=Connection().get_connection())

        # Call the Sheets API
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                     range=config.range_raw).execute()

        # Удаление юзеров из таблицы "Текущий Ивент"
        for index, user_id in enumerate(result['values']):
            if len(user_id) > 0 and user_id[4] in list_delete:
                service.spreadsheets().values().clear(spreadsheetId=sheet_id,
                                                      range=f"A{index + 1}:I{index + 1}").execute()

    def create_report(self):
        pass

    @staticmethod
    def change_status(user_id, user_status):
        """Изменение статуса Админ/Юзер в таблице "Участники Волонтёрства" """

        # Вызов Google Sheets API
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                        range=config.range_raw).execute()['values']
        for index, cell in enumerate(vol_sheet):
            if len(cell) > 0 and cell[4] == user_id:
                status_value = ((f"{user_status}",),)
                status_range_body = {'majorDimension': 'ROWS', 'values': status_value}

                # Изменение переменной цели в таблице:"Участники Волонтёрства".
                service.spreadsheets().values().update(spreadsheetId=config.sheet_vol_id,
                                                       range=f"H{index + 1}",
                                                       valueInputOption=config.raw_value_input_option,
                                                       body=status_range_body).execute()

    @staticmethod
    def check_status(user_id):
        # Вызов Google Sheets API
        service = build('sheets', 'v4', credentials=Connection().get_connection())
        vol_sheet = service.spreadsheets().values().get(spreadsheetId=config.sheet_vol_id,
                                                        range=config.range_raw).execute()['values']
        for index, cell in enumerate(vol_sheet):
            if len(cell) > 0 and cell[4] == user_id:
                if len(cell) > 0 and cell[7] == 'admin':
                    return True
        return False
