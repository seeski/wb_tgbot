import json, validators
from environs import Env
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, PhotoSize
from lexicon.lexicon_ru import lexicon_ru
from keyboards.kerboards import *
from services.states import PostForm
from services.decorators import main_chat, cancel_message
from aiogram.fsm.context import FSMContext

from db.models import session, User, Post
from services.factories import HasTariffCallbackFactory

router = Router()
env = Env()
env.read_env()
yootoken = env('YOOTOKEN')
owners = json.loads(env('OWNER_ID'))
moders = json.loads(env('MODER_ID'))


# не забыть настроить доступ к админке
@router.message(CommandStart())
@main_chat
async def process_start_command(message: Message, *args, **kwargs):
    try:
        user_id = message.from_user.id
        user_exist = session.query(User).filter(User.tg_id == user_id).first()
        if not user_exist:
            print('создание нового пользователя')
            new_user = User(tg_id=message.from_user.id, tariffs_data=json.dumps([]))
            session.add(new_user)
            session.commit()

        if user_id in owners or user_id in moders:
            staff = True
        else:
            staff = False

        await message.answer(lexicon_ru['user_start'], reply_markup=rules_info_kb())
        await message.answer(lexicon_ru['home'], reply_markup=start_kb(user_id))
    except Exception as e:
        session.rollback()
        await message.answer(text=f'произошла ошибка в функции process_start_command {e.__name__} {e}')

    finally:
        session.close()


@router.message(F.text == 'Правила')
@main_chat
async def rules(message: Message, *args, **kwargs):
    await message.answer(text=lexicon_ru['rules'], reply_markup=rules_info_kb())
    await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))


@router.message(F.text == 'Главная')
@main_chat
async def home(message: Message, *args, **kwargs):
    await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))


@router.message(F.text == 'Мои тарифы')
@main_chat
async def my_tariffs(message: Message, *args, **kwargs):
    try:
        text = lexicon_ru['my_tariffs']
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        tariffs_data = json.loads(user.tariffs_data)
        if not tariffs_data:
            text += lexicon_ru['has_no_tariffs']
            await message.answer(text=text, reply_markup=start_kb(user_id=message.from_user.id))
        else:
            for tariff_data in tariffs_data:
                text += lexicon_ru['my_tariff_template'].format(
                    tariff_data['name'], tariff_data['duration'], tariff_data['frequency']
                )

            kb = my_tariffs_kb(tariffs_data)
            await message.answer(text=text, reply_markup=kb)
    except Exception as e:
        session.rollback()
        await message.answer(text="произошла ошибка в функции my_tariffs")
    finally:
        session.close()


@router.pre_checkout_query()
@main_chat
async def pre_checkout(pre_checkout_query: PreCheckoutQuery, *args, **kwargs):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
@main_chat
async def successful_payment(message: Message, *args, **kwargs):
    try:
        if 'subscription' in message.successful_payment.invoice_payload:
            user = session.query(User).filter(User.tg_id == message.from_user.id).first()
            tariffs_data = json.loads(user.tariffs_data)
            payload = message.successful_payment.invoice_payload.split(':')
            new_tariff_data = {
                'name': payload[1],
                'frequency': int(payload[2]),
                'duration': int(payload[3])
            }
            tariffs_data.append(new_tariff_data)
            user.tariffs_data = json.dumps(tariffs_data)
            session.commit()
        await message.answer(text='Оплата прошла успешно', reply_markup=start_kb(user_id=message.from_user.id))
    except Exception as e:
        session.rollback()
        await message.answer(text='Произошла ошибка в функции successful_payment')
    finally:
        session.close()


@router.callback_query(HasTariffCallbackFactory.filter())
@main_chat
async def create_post(callback: CallbackQuery, state: FSMContext, *args, **kwargs):
    await state.set_state(PostForm.tariff_data)
    await state.update_data(tariff_data=callback.data)
    await state.set_state(PostForm.name)
    await callback.message.answer(text=lexicon_ru['enter_header'], reply_markup=cancel_kb())


@router.message(PostForm.name)
@cancel_message
@main_chat
async def enter_post_name(message: Message, state: FSMContext, *args, **kwargs):
    try:
        if len(message.text) <= 3 or len(message.text) > 50:
            await message.answer('Количество символов не соответствует правилам, попробуйте еще раз')

        # elif message.text == 'Отмена':
        #     await state.clear()
        #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))

        else:
            await state.update_data(name=message.text)
            await state.set_state(PostForm.desc)
            await message.answer(
                'Отлично! Теперь введите описание для вашего поста. Ограничение по символам - не менее 50 и не более 500')
    except Exception as e:
        await message.answer(text="Данные введены некоректно, повторите попытку")


@router.message(PostForm.desc)
@cancel_message
@main_chat
async def enter_post_desc(message: Message, state: FSMContext, *args, **kwargs):
    if message.text:
        m_len = len(message.text)
        if m_len < 50 or m_len > 500:
            await message.answer(text=lexicon_ru['wrong_desc_len'].format(m_len))

    # elif message.text == 'Отмена':
    #     await state.clear()
    #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))

        else:
            await state.update_data(desc=message.text)
            await state.set_state(PostForm.link)
            await message.answer(text=lexicon_ru['enter_link'])
    else:
        await message.answer(text="Данные введены некоректно, попробуйте еще раз")


@router.message(PostForm.link)
@cancel_message
@main_chat
async def enter_post_link(message: Message, state: FSMContext, *args, **kwargs):

    if message.text and message.text.startswith('@'):
        await state.update_data(link=message.text)
        await state.set_state(PostForm.photo)
        await message.answer(text=lexicon_ru['enter_photo'])

    else:
        await message.answer(text=lexicon_ru['wrong_link_entered'])

@router.message(PostForm.photo)
@cancel_message
@main_chat
async def enter_post_photo(message: Message, state: FSMContext, *args, **kwargs):
    # if message.text == 'Отмена':
    #     await state.clear()
    #     await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))

    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo=photo_id)
        await state.set_state(PostForm.confirmation)
        data = await state.get_data()
        await message.answer_photo(
            photo=data['photo'],
            caption=lexicon_ru['post_template'].format(data['name'], data['desc'], data['link'])
        )
        tariff_callback = data['tariff_data'].split(":")
        await message.answer(lexicon_ru['post_demo'].format(
            tariff_callback[1], tariff_callback[2], tariff_callback[3]
        ), reply_markup=continue_kb())
    else:
        await message.answer('Для создания поста обязательно использование фото. Пожалуйста, отправьте мне фотографию')


@router.message(PostForm.confirmation)
@cancel_message
@main_chat
async def confirm_post(message: Message, state: FSMContext, *args, **kwargs):
    try:
        if message.text == 'Продолжить':
            data = await state.get_data()
            # убираем выбранный пользователем тариф из всех доступных пользователю
            tariff_data = data['tariff_data'].split(':')
            tariff = {
                'name': tariff_data[1],
                'frequency': int(tariff_data[2]),
                'duration': int(tariff_data[3])
            }
            user = session.query(User).filter(User.tg_id == message.from_user.id).first()
            user_tariffs: list = json.loads(user.tariffs_data)
            user_tariffs.remove(tariff)
            user.tariffs_data = json.dumps(user_tariffs)

            post = Post(
                header=data['name'],
                desc=data['desc'],
                link=data['link'],
                photo_id=data['photo'],
                user=message.from_user.id,
                tariff_name=tariff['name'],
                frequency=tariff['frequency'],
                duration=tariff['duration'],
                amount=tariff['frequency'] * tariff['duration']
            )
            session.add(post)
            session.commit()
            await state.clear()
            await message.answer(text=lexicon_ru['post_successfully_created'], reply_markup=start_kb(user_id=message.from_user.id))
        else:
            await message.answer(text=lexicon_ru['wrong_confirmation_entered'])
    except Exception as e:
        session.rollback()
        await message.answer(text="произошла ошибка в функции confirm_post")
    finally:
        session.close()