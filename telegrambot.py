import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from admin import *
import markups as nav
import config


class ClientState(StatesGroup):
    """Хранит на каком этапе диалога находится юзер"""
    SET_NICKNAME = State()
    SET_GROUP = State()
    SET_PHONE = State()
    SET_TELEGRAM = State()
    CHANGE_NICKNAME = State()
    CHANGE_GROUP = State()
    CHANGE_PHONE = State()
    CHANGE_TELEGRAM = State()

    CREATE_EVENT = State()
    DELETE_USER_FIRST = State()
    DELETE_USER_SECOND = State()
    CANCEL_EVENT = State()
    CONFIRM_EVENT = State()

    EVENT_NAME = State()
    EVENT_DATE = State()
    EVENT_TIME = State()
    EVENT_VENUE = State()
    EVENT_TYPE = State()
    EVENT_SCORE = State()

    USER_STATE = State()
    ADMIN_STATE = State()


storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dispatcher = Dispatcher(bot, storage=storage)
authorization_list = []
create_event_list = []
delete_user_list = []


@dispatcher.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext) -> None:
    if str(message.from_user.id) not in Admin.get_value_data_sheet(config.sheet_vol_id, config.range_user_id):
        await bot.send_message(message.from_user.id, config.welcome_text)
        await state.set_state(ClientState.SET_NICKNAME)
    else:
        await bot.send_message(message.from_user.id, "Добрий день {0.first_name}".format(message.from_user),
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)


@dispatcher.message_handler(state=ClientState.SET_NICKNAME)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text is not None:
        authorization_list.append(str(message.text))
        await bot.send_message(message.from_user.id, 'Напишіть свою групу у форматі: "2-21-18"')
        await state.set_state(ClientState.SET_GROUP)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.SET_GROUP)
async def set_group(message: types.Message, state: FSMContext) -> None:
    if message.text is not None and message.text.replace('-', '').isdigit() and\
            '-' in message.text and len(message.text) >= 5:
        authorization_list.append(str(message.text))
        await bot.send_message(message.from_user.id, 'Напишіть свій телефон у форматі: "38**********"')
        await state.set_state(ClientState.SET_PHONE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.SET_PHONE)
async def set_phone(message: types.Message, state: FSMContext) -> None:
    if message.text is not None:
        if message.text is not None and 13 > len(message.text) >= 10 and message.text.isdigit():
            authorization_list.append(str(message.text))
            await bot.send_message(message.from_user.id, 'Напишіть свій телеграм у форматі: "@Mishka"')
            await state.set_state(ClientState.SET_TELEGRAM)
        else:
            await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.SET_TELEGRAM)
async def set_telegram(message: types.Message, state: FSMContext) -> None:
    if message.text is not None and '@' in message.text and len(message.text) >= 4:
        authorization_list.append(str(message.text))
        User.authorization(user_name=authorization_list[0], user_group=authorization_list[1],
                           user_phone=authorization_list[2], user_telegram=authorization_list[3],
                           user_id=str(message.from_user.id))
        time.sleep(0.25)
        await bot.send_message(message.from_user.id, 'Реєстрація пройшла успішно')
        await bot.send_message(message.from_user.id, "Добрий день {0.first_name}".format(message.from_user),
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)


@dispatcher.message_handler(state=ClientState.USER_STATE)
async def user(message: types.Message, state: FSMContext) -> None:
    dict_name_id = nav.get_dict_sheet_param(list_id=config.sheet_current_events_id, first_range_list=config.range_name,
                                            second_range_list=config.range_sheet_id)
    if message.text == '☤ Рейтинг Студентів':
        await bot.send_message(message.from_user.id, User.view_others_history())

    elif message.text == '🔥 Свій Рейтинг':
        await bot.send_message(message.from_user.id, User.view_own_history(str(message.from_user.id)))

    elif message.text == '🚀 Запис на Івент':
        await bot.send_message(message.from_user.id, '🚀 Запис на Івент',
                               reply_markup=nav.participate_keyboard())
    elif dict_name_id.get(f"{message.text}") is not None:
        if User.check_presence(participate_sheet_id=dict_name_id.get(f"{message.text}"),
                               user_id=str(message.from_user.id)) is True:
            await bot.send_message(message.from_user.id, "Ви вже зареєстровані 😉")
        else:
            await bot.send_message(message.from_user.id, "Успішно зареєструвалися ☺")
            User.participate_event(participate_sheet_id=dict_name_id.get(f"{message.text}"),
                                   user_id=str(message.from_user.id))

    elif message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)

    elif message.text == '✨ Особисті дані':
        await bot.send_message(message.from_user.id, 'Ваші дані:')
        await bot.send_message(message.from_user.id, User.give_own_data(user_id=str(message.from_user.id)),
                               reply_markup=nav.changeMenu)
    elif message.text == 'Змінити ФІО':
        await bot.send_message(message.from_user.id, 'Вкажіть нове ФІО:')
        await state.set_state(ClientState.CHANGE_NICKNAME)
    elif message.text == 'Змінити Группу':
        await bot.send_message(message.from_user.id, 'Вкажіть нову группу:')
        await state.set_state(ClientState.CHANGE_GROUP)
    elif message.text == 'Змінити Номер':
        await bot.send_message(message.from_user.id, 'Вкажіть новий номер:')
        await state.set_state(ClientState.CHANGE_PHONE)
    elif message.text == 'Змінити Телеграм':
        await bot.send_message(message.from_user.id, 'Вкажіть новий телеграм')
        await state.set_state(ClientState.CHANGE_TELEGRAM)
    elif message.text == 'Змінити Анонимність🙈':
        await bot.send_message(message.from_user.id, "Чи хочите змінити свою анонімність?",
                               reply_markup=nav.anonymMenu)
    elif message.text == 'Сховати свій рейтинг🙉':
        User.change_anonymity(str(message.from_user.id), "TRUE")
        await bot.send_message(message.from_user.id, "Ваші дані приховані від інших у загальному рейтингу✨")
    elif message.text == 'Розкрити свій рейтинг🙈':
        User.change_anonymity(str(message.from_user.id), "FALSE")
        await bot.send_message(message.from_user.id, "Ваші дані відкриті для інших у загальному рейтингу✨")
    elif message.text == '✍ Пропозиції':
        await bot.send_message(message.from_user.id, config.boss_text,
                               reply_markup=nav.bossMenu)
    elif message.text == '👾TOP SECRET👽':
        if Admin.check_status(str(message.from_user.id)):
            await state.set_state(ClientState.ADMIN_STATE)
            time.sleep(0.1)
            await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
        else:
            await bot.send_message(message.from_user.id, "Не жамкай тут, мені ще цю кнопку мити 😡")


@dispatcher.message_handler(state=ClientState.CHANGE_NICKNAME)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text is not None:
        User.change_setting(user_id=str(message.from_user.id), user_range="A",
                            user_setting=str(message.text))
        await bot.send_message(message.from_user.id, 'Дані було успішно змінено😎\nТепер ваші дані такі:')
        await bot.send_message(message.from_user.id, User.give_own_data(user_id=str(message.from_user.id)))
        await state.set_state(ClientState.USER_STATE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.CHANGE_GROUP)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text is not None and message.text.replace('-', '').isdigit() and\
            '-' in message.text and len(message.text) >= 5:
        User.change_setting(user_id=str(message.from_user.id), user_range="B",
                            user_setting=str(message.text))
        await bot.send_message(message.from_user.id, 'Дані було успішно змінено😎\nТепер ваші дані такі:')
        await bot.send_message(message.from_user.id, User.give_own_data(user_id=str(message.from_user.id)))
        await state.set_state(ClientState.USER_STATE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.CHANGE_PHONE)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text is not None and 13 > len(message.text) >= 10 and message.text.isdigit():
        User.change_setting(user_id=str(message.from_user.id), user_range="C",
                            user_setting=str(message.text))
        await bot.send_message(message.from_user.id, 'Дані було успішно змінено😎\nТепер ваші дані такі:')
        await bot.send_message(message.from_user.id, User.give_own_data(user_id=str(message.from_user.id)))
        await state.set_state(ClientState.USER_STATE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.CHANGE_TELEGRAM)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text is not None and '@' in message.text and len(message.text) >= 4:
        User.change_setting(user_id=str(message.from_user.id), user_range="D",
                            user_setting=str(message.text))
        await bot.send_message(message.from_user.id, 'Дані було успішно змінено😎\nТепер ваші дані такі:')
        await bot.send_message(message.from_user.id, User.give_own_data(user_id=str(message.from_user.id)))
        await state.set_state(ClientState.USER_STATE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


@dispatcher.message_handler(state=ClientState.ADMIN_STATE)
async def admin(message: types.Message, state: FSMContext) -> None:

    if message.text == '⬅ Головне меню':
        await state.set_state(ClientState.USER_STATE)
        time.sleep(0.1)
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
    elif message.text == '👾TOP SECRET👽':
        if Admin.check_status(str(message.from_user.id)):
            await state.set_state(ClientState.ADMIN_STATE)
            await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
        else:
            await bot.send_message(message.from_user.id, "Не жамкай тут, мені ще цю кнопку мити 😡")
    elif message.text == 'Створити Івент💗':
        await bot.send_message(message.from_user.id, 'Напишіть назву Івенту')
        await state.set_state(ClientState.EVENT_NAME)
    # elif message.text == 'Відзначити участників💘':
    #     await bot.send_message(message.from_user.id, 'Виберіть Івент, у якому хочете відзначити учасників💘',
    #                            reply_markup=nav.event_keyboard())
    #     await state.set_state(ClientState.DELETE_USER_FIRST)
    elif message.text == 'Відминити Івент💔':
        await bot.send_message(message.from_user.id, 'Відминити Івент💔',
                               reply_markup=nav.event_keyboard())
        await state.set_state(ClientState.CANCEL_EVENT)
    elif message.text == 'Завершити Івент❤':
        await bot.send_message(message.from_user.id, 'Завершити Івент❤',
                               reply_markup=nav.event_keyboard())
        await state.set_state(ClientState.CONFIRM_EVENT)


@dispatcher.message_handler(state=ClientState.CANCEL_EVENT)
async def cancel_events(message: types.Message, state: FSMContext) -> None:
    dict_name_id = nav.get_dict_sheet_param(list_id=config.sheet_current_events_id, first_range_list=config.range_name,
                                            second_range_list=config.range_sheet_id)
    if message.text == '👾TOP SECRET👽':
        if Admin.check_status(str(message.from_user.id)):
            await state.set_state(ClientState.ADMIN_STATE)
            await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
    elif dict_name_id.get(str(message.text)) is not None:
        Admin.cancel_event(destruction_spreadsheet_id=dict_name_id.get(str(message.text)))
        await state.set_state(ClientState.ADMIN_STATE)
        await bot.send_message(message.from_user.id, 'Івент Відмінено💔')
    elif dict_name_id.get(str(message.text)) is None:
        await bot.send_message(message.from_user.id, 'Івент вже відмінено❤')


@dispatcher.message_handler(state=ClientState.CONFIRM_EVENT)
async def confirm_events(message: types.Message, state: FSMContext) -> None:
    dict_name_id = nav.get_dict_sheet_param(list_id=config.sheet_current_events_id, first_range_list=config.range_name,
                                            second_range_list=config.range_sheet_id)
    if message.text == '👾TOP SECRET👽':
        if Admin.check_status(str(message.from_user.id)):
            await state.set_state(ClientState.ADMIN_STATE)
            await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
    elif dict_name_id.get(str(message.text)) is not None:
        present = Admin.confirm_event(destruction_spreadsheet_id=dict_name_id.get(str(message.text)))
        if present is True:
            await bot.send_message(message.from_user.id, 'Івент завершено❤')
            await state.set_state(ClientState.ADMIN_STATE)
        else:
            await bot.send_message(message.from_user.id, 'Івент не має учасників, тому його не'
                                                         ' можна завершити - лише видалити')
            await state.set_state(ClientState.ADMIN_STATE)
    elif dict_name_id.get(str(message.text)) is None:
        await bot.send_message(message.from_user.id, 'Івент вже завершен❤')


@dispatcher.message_handler(state=ClientState.EVENT_NAME)
async def set_nickname(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None:
        create_event_list.append(str(message.text))
        await bot.send_message(message.from_user.id, 'Напишіть дату проведення івенту')
        await state.set_state(ClientState.EVENT_DATE)



@dispatcher.message_handler(state=ClientState.EVENT_DATE)
async def set_date(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None:
        create_event_list.append(str(message.text))
        await bot.send_message(message.from_user.id, 'Напишіть час проведення івенту')
        await state.set_state(ClientState.EVENT_TIME)


@dispatcher.message_handler(state=ClientState.EVENT_TIME)
async def set_time(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None:
        create_event_list.append(str(message.text))

        await bot.send_message(message.from_user.id, 'Напишіть місце проведення івенту')
        await state.set_state(ClientState.EVENT_VENUE)


@dispatcher.message_handler(state=ClientState.EVENT_VENUE)
async def set_venue(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None:
        create_event_list.append(str(message.text))
        await bot.send_message(message.from_user.id, 'Напишіть тип івенту')
        await state.set_state(ClientState.EVENT_TYPE)


@dispatcher.message_handler(state=ClientState.EVENT_TYPE)
async def set_type(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None:
        create_event_list.append(str(message.text))
        await bot.send_message(message.from_user.id,
                               'Напишіть кілкість балів. Число повинно бути з розділовим знаком "."\n'
                               'Приклад: 1.0 чи 0.25 та інше')
        await state.set_state(ClientState.EVENT_SCORE)


@dispatcher.message_handler(state=ClientState.EVENT_SCORE)
async def set_score(message: types.Message, state: FSMContext) -> None:
    if message.text == '⬅ Головне меню':
        await bot.send_message(message.from_user.id, '⬅ Головне меню',
                               reply_markup=nav.mainMenu)
        await state.set_state(ClientState.USER_STATE)
    elif message.text is not None and message.text.replace('.', '').isdigit() and '.' in message.text:
        create_event_list.append(str(message.text))
        Admin.add_event(create_event_list[0], create_event_list[1], create_event_list[2],
                        create_event_list[3], create_event_list[4], create_event_list[5],)
        await bot.send_message(message.from_user.id, 'Завершення')
        create_event_list.clear()
        await state.set_state(ClientState.ADMIN_STATE)
    else:
        await bot.send_message(message.from_user.id, 'Неправильний формат. Спробуйте знову.')


# @dispatcher.message_handler(state=ClientState.DELETE_USER_FIRST)
# async def delete_users_first(message: types.Message, state: FSMContext) -> None:
#     dict_name_id = nav.get_dict_sheet_param(list_id=config.sheet_current_events_id,
#                                             first_range_list=config.range_name,
#                                             second_range_list=config.range_sheet_id)
#     if message.text == '👾TOP SECRET👽':
#         if Admin.check_status(str(message.from_user.id)):
#             await state.set_state(ClientState.ADMIN_STATE)
#             await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
#
#     elif dict_name_id.get(str(message.text)) is not None:
#         present = Admin.get_present(sheet_vol_id=str(dict_name_id.get(str(message.text))))
#         if present is not False:
#             await bot.send_message(message.from_user.id,
#             Admin.get_name_and_id(sheet_id=dict_name_id.get(str(message.text))))
#             delete_user_list.append(str(dict_name_id.get(str(message.text))))
#             await bot.send_message(message.from_user.id, 'Напишіть через кому ID із переченя тих учасників, яких'
#                                                          ' НЕ БУЛО на заході. Приклад: "53234,421421,55112"'
#                                                          'або "155353, 52141, 53153"')
#             await state.set_state(ClientState.DELETE_USER_SECOND)
#
#         elif present is False:
#             await bot.send_message(message.from_user.id, 'Івент не має учасників.')
#             await state.set_state(ClientState.ADMIN_STATE)
#
#
# @dispatcher.message_handler(state=ClientState.DELETE_USER_SECOND)
# async def delete_users_second(message: types.Message, state: FSMContext) -> None:
#     dict_name_id = nav.get_dict_sheet_param(list_id=config.sheet_current_events_id,
#                                             first_range_list=config.range_name,
#                                             second_range_list=config.range_sheet_id)
#     if message.text == '👾TOP SECRET👽':
#         if Admin.check_status(str(message.from_user.id)):
#             await state.set_state(ClientState.ADMIN_STATE)
#             await bot.send_message(message.from_user.id, "✨Вас допущено до таємниць✨", reply_markup=nav.adminMenu)
#     elif message.text is not None and str(message.text).replace(',', '').isdigit():
#         list_del = str(message.text).split(',')
#         Admin.delete_users(sheet_id=delete_user_list[0], list_delete=list_del)
#         await bot.send_message(message.from_user.id, "Зміни зроблені.", reply_markup=nav.adminMenu)
#
#         await state.set_state(ClientState.ADMIN_STATE)
#     else:
#         await bot.send_message(message.from_user.id, "Неправильний формат. Спробуйте знову.")


if __name__ == '__main__':
    executor.start_polling(dispatcher)
