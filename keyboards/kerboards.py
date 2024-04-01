from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config_data.config import TariffInfo
from services.factories import HasTariffCallbackFactory, ChangeTariffCallbackFactory
import json
from environs import Env

env = Env()
env.read_env()
owners = json.loads(env('OWNER_ID'))
moders = json.loads(env('MODER_ID'))
def start_kb(user_id):

    staff = user_id in moders or user_id in owners
    kb = ReplyKeyboardBuilder()
    kb.button(text='Тарифы').button(text='Мои тарифы').button(text='Главная').button(text='Правила')

    # Если юезр имеет стафф статус, то в функцию передается аргумент True
    # и добавляется новая кнопка для перехода в админ панель
    if staff:
        kb.button(text='Админ')
        kb.adjust(2, 2, 1)
    else:
        kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)



def tariffs_kb():
    buttons = [KeyboardButton(text=tariff) for tariff in TariffInfo.get_tariffs()]

    back_button = KeyboardButton(text='Отмена')
    buttons.append(back_button)
    print(len(buttons))
    print(buttons)
    kb = ReplyKeyboardBuilder()
    for i in range(0, 6, 2):
        kb.row(*[
            buttons[i], buttons[i+1]
        ])

    return kb.as_markup(resize_keyboard=True)


def tariffs_info_kb():
    button = InlineKeyboardButton(
        text='Читать',
        url='https://telegra.ph/Tarify-03-13-2'
    )
    kb = InlineKeyboardBuilder()
    kb.row(*[button])
    return kb.as_markup()

def rules_info_kb():
    button = InlineKeyboardButton(
        text='Читать',
        url='https://telegra.ph/Pravila-03-29-64'
    )
    kb = InlineKeyboardBuilder()
    kb.row(*[button])
    return kb.as_markup()


def frequency_kb():
    buttons = [KeyboardButton(
        text=str(i)
    ) for i in TariffInfo.frequency]
    buttons.append(
        KeyboardButton(text='Отмена')
    )

    kb = ReplyKeyboardBuilder()
    kb.row(*buttons[:5])
    kb.row(*buttons[5:])
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def my_tariffs_kb(tariffs_data):
    kb = InlineKeyboardBuilder()
    buttons = []
    for data in tariffs_data:
        callback_data = HasTariffCallbackFactory(tariff_name=data["name"], frequency=data["frequency"], duration=data["duration"])
        button = InlineKeyboardButton(
            text=f'{data["name"]} {data["frequency"]}×{data["duration"]}',
            callback_data=callback_data.pack()
        )
        buttons.append(button)
    kb.row(*buttons, width=1)
    return kb.as_markup()


def continue_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Продолжить').button(text='Отмена')
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def admin_kb(user_id):
    kb = ReplyKeyboardBuilder()
    kb.button(text='Посты').button(text='Выйти')
    if user_id in owners:
        kb.button(text='Цены на тарифы')
        kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def check_post_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text='✅').button(text='❌').button(text='Отмена')
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def change_tariffs_kb(tariffs: dict):
    kb = InlineKeyboardBuilder()
    buttons = []
    for tariff in tariffs:
        callback_data = ChangeTariffCallbackFactory(name=tariff, price=tariffs[tariff])
        button = InlineKeyboardButton(
            text=f'{tariff} {tariffs[tariff]} руб.', callback_data=callback_data.pack()
        )
        buttons.append(button)

    kb.row(*buttons, width=1)
    return kb.as_markup()

def cancel_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    return kb.as_markup(resize_keyboard=True)

rmk = ReplyKeyboardRemove()