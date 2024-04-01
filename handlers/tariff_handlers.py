import json
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.labeled_price import LabeledPrice
from services.states import SubInfoForm
from services.decorators import main_chat, cancel_message
from lexicon.lexicon_ru import lexicon_ru
from keyboards.kerboards import tariffs_kb, frequency_kb, rmk, start_kb, cancel_kb
from config_data.config import TariffInfo
from environs import Env
from db.models import session, User, Tariff

router = Router()
env = Env()
env.read_env()
yootoken = env('YOOTOKEN')

# @tariff_router.message(F.text.in_([f'Тариф {i}' for i in range(1, 6)]))


@router.message(F.text == 'Тарифы')
@main_chat
async def tariffs(message: Message, state: FSMContext, *args, **kwargs):
    await state.set_state(SubInfoForm.tariff)
    await message.answer(text=lexicon_ru['tariffs_action'], reply_markup=tariffs_kb())


@router.message(SubInfoForm.tariff)
@cancel_message
@main_chat
async def define_tariff(message: Message, state: FSMContext, *args, **kwargs):
    if message.text in TariffInfo.get_tariffs():
        await state.update_data(tariff=message.text)
        await state.set_state(SubInfoForm.frequency)
        await message.answer(text='Чтобы ввести желаемую частоту публикаци, нажмите на кнопку', reply_markup=frequency_kb())

    # elif message.text == 'Отмена':
    #     await state.clear()
    #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))

    else:
        await message.answer(text='Выбарнного тарифа нет в списке')


@router.message(SubInfoForm.frequency)
@cancel_message
@main_chat
async def define_frequency(message: Message, state: FSMContext, *args, **kwargs):
    if message.text.isdigit() and int(message.text) in TariffInfo.frequency:
        await state.update_data(frequency=int(message.text))
        await state.set_state(SubInfoForm.duration)
        await message.answer(text='Введите количество дней, в течение которого хотите, чтобы публиковалось ваше объявление', reply_markup=cancel_kb())

    # elif message.text == 'Отмена':
    #     await state.clear()
    #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))

    else:
        await message.answer('Нажмите на кнопку или введите число, которое представлено на панели с кнопками')


@router.message(SubInfoForm.duration)
@cancel_message
@main_chat
async def define_duration(message: Message, state: FSMContext, *args, **kwargs):

    if message.text.isdigit():
        data = await state.get_data()
        await message.answer(text='Форма на тариф была успешно заполнена')
        tariffs_info = TariffInfo.get_tariffs()
        # если цена за пост != 0, тогда содаем ордер, потому что цена будет > 0
        if data['tariff'] in tariffs_info and tariffs_info.get(data['tariff']):
            tariff_price = TariffInfo.get_tariffs()
            tariff_price = tariff_price[data['tariff']]
            amount = int(data['frequency']) * tariff_price * int(message.text) * 100
            if amount < 60 * 100:
                await message.answer(text='Минимальная сумма на оплату - 60 рублей. Выберите другую частоту и/или продолжительность публикации', reply_markup=frequency_kb())
                await state.set_state(SubInfoForm.frequency)
            else:
                await message.answer_invoice(
                    title='Оплата тарифа',
                    description=f'Тариф "{data["tariff"]}" на {message.text} дней',
                    payload=f'subscription:{data["tariff"]}:{data["frequency"]}:{message.text}',
                    provider_token=yootoken,
                    currency='RUB',
                    start_parameter='bot',
                    prices=[LabeledPrice(amount=amount, label='руб.')],
                )

        # если цена за пост бесплатная, то не создаем никакой оплаты и просто добавляем тариф во владение к пользователю
        else:
            user = session.query(User).filter(User.tg_id == message.from_user.id).first()
            tariffs_data = json.loads(user.tariffs_data)
            new_tariff_data = {
                'name': data['tariff'],
                'frequency': int(data['frequency']),
                'duration': int(message.text)
            }
            tariffs_data.append(new_tariff_data)
            user.tariffs_data = json.dumps(tariffs_data)
            session.commit()
            await message.answer(text=lexicon_ru['successful_free_pay'], reply_markup=start_kb(user_id=message.from_user.id))

    # elif message.text == 'Отмена':
    #     await state.clear()
    #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_userid))

    else:
        await message.answer(text='Введите кол-во дней')