from aiogram.fsm.state import StatesGroup, State


class SubInfoForm(StatesGroup):
    tariff = State()
    frequency = State()
    duration = State()


class PostForm(StatesGroup):
    tariff_data = State()
    name = State()
    desc = State()
    link = State()
    photo = State()
    confirmation = State()

class CheckPost(StatesGroup):

    post_id = State()
    allowed = State()


class TariffPrice(StatesGroup):
    tariff_data = State()
    price = State()