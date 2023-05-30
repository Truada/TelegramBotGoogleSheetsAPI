from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from admin import *

btnMain = KeyboardButton('⬅ Головне меню')
btnSecret = KeyboardButton('👾TOP SECRET👽')
# Main Menu
btnParticipation = KeyboardButton('🚀 Запис на Івент')
btnRating = KeyboardButton('☤ Рейтинг Студентів')
btnChangeSettings = KeyboardButton('✨ Особисті дані')
btnScore = KeyboardButton('🔥 Свій Рейтинг')
btnComplain = KeyboardButton('✍ Пропозиції')


mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnParticipation, btnScore, btnRating,
                                                         btnChangeSettings, btnComplain, btnSecret)


# Предложка
btnSecondBoss = InlineKeyboardButton(text='Зам. голови студентського самоврядування', url="https://t.me/KeT_ToP")
btnFirstBoss = InlineKeyboardButton(text='Голова студентського самоврядування', url="https://t.me/VolKNMUBot")
bossMenu = InlineKeyboardMarkup(resize_keyboard=True).add(btnSecondBoss, btnFirstBoss)
# Change Settings Menu
btnChangeName = KeyboardButton('Змінити ФІО')
btnChangeGroup = KeyboardButton('Змінити Группу')
btnChangePhone = KeyboardButton('Змінити Номер')
btnChangeTelegram = KeyboardButton('Змінити Телеграм')
btnChangeAnonym = KeyboardButton('Змінити Анонимність🙈')
changeMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnChangeName, btnChangeGroup, btnChangePhone,
                                                           btnChangeTelegram, btnChangeAnonym, btnMain)
# Anonym Menu
btnTrueAnonym = KeyboardButton('Сховати свій рейтинг🙉')
btnFalseAnonym = KeyboardButton('Розкрити свій рейтинг🙈')
anonymMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnTrueAnonym, btnFalseAnonym, btnMain)
# Admin Menu
btnCreateEvent = KeyboardButton('Створити Івент💗')
btnDeleteUsers = KeyboardButton('Відзначити участників💘')
btnCancelEvent = KeyboardButton('Відминити Івент💔')
btnConfirmEvent = KeyboardButton('Завершити Івент❤')
adminMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnCreateEvent,
                                                          btnConfirmEvent, btnCancelEvent, btnMain)

# Функция берёт два пункта таблицы мёрджит их и создаёт из них словарь


def get_dict_sheet_param(list_id, first_range_list, second_range_list):
    list1 = Admin.get_value_data_sheet(list_id,  first_range_list)
    list2 = Admin.get_value_data_sheet(list_id,  second_range_list)
    return dict(zip(list1, list2))

# Функции, которые передают специфические клавиатуры с динамическими данными


def participate_keyboard():
    list1 = Admin.get_value_data_sheet(config.sheet_current_events_id, "A2:A")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*list1, btnMain)
    return keyboard


def event_keyboard():
    list1 = Admin.get_value_data_sheet(config.sheet_current_events_id, "A2:A")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*list1, btnSecret)
    return keyboard


def delete_keyboard(sheet_id):
    list1 = Admin.get_value_data_sheet(sheet_id, "A2:A")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*list1, btnMain)
    return keyboard
