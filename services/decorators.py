from config_data.config import EnvData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import lexicon_ru
from keyboards.kerboards import admin_kb, start_kb



# проверяет чат на соответствие id основного чата
# В основном чате, куда скидываются посты, бот не должен отвечать ничего и ни на что
# только публикация, закрепы и сторис
def main_chat(func):
    async def wrapper(*args, **kwargs):

        if kwargs.get('event_chat') and kwargs.get('event_chat').id in EnvData.main_chats:
            print('returning None')
            return None
        else:
            return await func(*args, **kwargs)
    return wrapper


def cancel_message(func):
    async def wrapper(*args, **kwargs):
        message: Message = args[0]
        state: FSMContext = kwargs['state']
        if message.text == 'Отмена':
            await state.clear()
            await message.answer(text=lexicon_ru['home'], reply_markup=start_kb(user_id=message.from_user.id))
        else:
            return await func(*args, **kwargs)
    return wrapper


def staff_cancel_message(func):
    async def wrapper(*args, **kwargs):
        message: Message = args[0]
        state: FSMContext = kwargs['state']
        if message.text == 'Отмена':
            await state.clear()
            await message.answer(text=lexicon_ru['home'], reply_markup=admin_kb(user_id=message.from_user.id))
        else:
            return await func(*args, **kwargs)

    return wrapper

def is_staff(func):
    async def wrapper(*args, **kwargs):
        print(args, 'args')
        message: Message = args[0]
        user_id = message.from_user.id
        if user_id not in EnvData.moders and user_id not in EnvData.owners:
            await message.answer(text='Недостаточно прав для доступа к админ панели :)')
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEENJNl_DaobOnLb1RCJqJ2gqgrO72HtgACtC4AAr650Eq7dYK3A-HYKzQE'
            )

        else:
            return await func(*args, **kwargs)

    return wrapper

def is_owner(func):
    async def wrapper(*args, **kwargs):
        message: Message = args[0]
        if message.from_user.id in EnvData.owners:
            return await func(*args, **kwargs)

        else:
            await message.answer(text='Недостаточно прав для доступа к админ панели :)')
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEENJNl_DaobOnLb1RCJqJ2gqgrO72HtgACtC4AAr650Eq7dYK3A-HYKzQE'
            )

    return wrapper


def is_owner_query(func):
    async def wrapper(*args, **kwargs):
        callback: CallbackQuery = args[0]
        if callback.from_user.id in EnvData.owners:
            return await func(*args, **kwargs)
        else:
            await callback.message.answer(text='Недостаточно прав для доступа к админ панели :)')
            await callback.message.answer_sticker(
                sticker='CAACAgIAAxkBAAEENJNl_DaobOnLb1RCJqJ2gqgrO72HtgACtC4AAr650Eq7dYK3A-HYKzQE'
            )
    return wrapper