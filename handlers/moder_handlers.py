import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import lexicon_ru
from keyboards.kerboards import *
from services.states import CheckPost, TariffPrice
from services.decorators import *
from aiogram.fsm.context import FSMContext
from db.models import session, User, Post
from environs import Env
from config_data.config import TariffInfo
from services.factories import ChangeTariffCallbackFactory
from db.models import Tariff

router = Router()
env = Env()
env.read_env()
owners = json.loads(env('OWNER_ID'))
moders = json.loads(env('MODER_ID'))


@router.message(F.text == 'Админ')
@is_staff
@main_chat
async def admin_panel(message: Message, *args, **kwargs):
    user_id = message.from_user.id
    if user_id in moders:
        await message.answer(text=lexicon_ru['welcome_to_admin_panel'].format('модератор'), reply_markup=admin_kb(user_id=user_id))
    else:
        await message.answer(text=lexicon_ru['welcome_to_admin_panel'].format('владелец'), reply_markup=admin_kb(user_id=user_id))

@router.message(F.text == 'Выйти')
@main_chat
async def exit_admin_panel(message: Message, *args, **kwargs):
    await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))


@router.message(F.text == 'Посты')
@is_staff
@main_chat
async def check_posts(message: Message, state: FSMContext, *args, **kwargs):
    post = session.query(Post).filter(Post.allowed == None).first()
    if post:
        await state.set_state(CheckPost.post_id)
        await state.update_data(post_id=post.id)
        await state.set_state(CheckPost.allowed)
        await message.answer_photo(
            photo=post.photo_id,
            caption=lexicon_ru['post_template'].format(post.header, post.desc, post.link) + f'\n\nтариф "{post.tariff_name}',
            reply_markup=check_post_kb()
        )
    else:
        await message.answer(text=lexicon_ru['no_posts_to_check'], reply_markup=admin_kb(user_id=message.from_user.id))


@router.message(CheckPost.allowed, F.text.in_(['❌', '✅']))
@staff_cancel_message
@is_staff
@main_chat
async def allow_post(message: Message, state: FSMContext, *args, **kwargs):
    if message.text == '✅' or message.text == '❌':
        data = await state.get_data()
        await state.clear()
        post_id = data['post_id']
        post = session.query(Post).filter(Post.id == post_id).first()
        if message.text == '✅':
            post.allowed = True
        else:
            post.allowed = False
        session.commit()
        new_post_to_allow = session.query(Post).filter(Post.allowed == None).order_by(Post.id).first()
        if new_post_to_allow:
            await state.set_state(CheckPost.post_id)
            await state.update_data(post_id=new_post_to_allow.id)
            await state.set_state(CheckPost.allowed)

            await message.answer_photo(
                photo=new_post_to_allow.photo_id,
                caption=lexicon_ru['post_template'].format(new_post_to_allow.header, new_post_to_allow.desc,
                                                           new_post_to_allow.link) + f'\n\nтариф "{new_post_to_allow.tariff_name}',
                reply_markup=check_post_kb()
            )
        else:
            await message.answer(lexicon_ru['no_posts_to_check'], reply_markup=start_kb(user_id=message.from_user.id))

    else:
        await message.answer(text='Нет такой команды. Нажмите на одну из кнопок', reply_markup=check_post_kb())


@router.message(F.text == 'Цены на тарифы')
@is_owner
@main_chat
async def tariffs_prices(message: Message, *args, **kwargs):
    await message.answer(text=lexicon_ru['admin_tariffs_price'], reply_markup=change_tariffs_kb(TariffInfo.get_tariffs()))

@router.callback_query(ChangeTariffCallbackFactory.filter())
@is_owner_query
async def select_tariff_to_change_price(callback_query: CallbackQuery, state: FSMContext, *args, **kwargs):
    await state.set_state(TariffPrice.tariff_data)
    await state.update_data(tariff_data=callback_query.data)
    await state.set_state(TariffPrice.price)
    tariff = callback_query.data.split(':')[1]
    text = lexicon_ru['change_tariff_price'].format(tariff)
    await callback_query.message.answer(text=text, reply_markup=cancel_kb())


@router.message(TariffPrice.price)
@staff_cancel_message
async def change_tariff_price(message: Message, state: FSMContext, *args, **kwargs):
    if message.text.isdigit():
        data = await state.get_data()
        tariff_data = data.get('tariff_data')
        tariff = session.query(Tariff).filter(Tariff.name == tariff_data.split(':')[1]).first()
        tariff.post_price = int(message.text)
        session.commit()
        await state.clear()
        await message.answer(text='Цена успешна изменена', reply_markup=admin_kb(user_id=message.from_user.id))
    else:
        await message.answer(text='Цена введена некоректно. Повторите попытку или нажмите на кнопку "Отмена"', reply_markup=cancel_kb())
