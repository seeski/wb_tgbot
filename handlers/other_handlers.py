from aiogram import Router
from aiogram.types import Message
from keyboards.kerboards import start_kb
from services.decorators import main_chat, cancel_message
from environs import Env
import json

router = Router()
env = Env()
env.read_env()
owners = json.loads(env('OWNER_ID'))
moders = json.loads(env('MODER_ID'))

@router.message()
@main_chat
async def any_message(message: Message, *args, **kwargs):
    await message.answer(text='Команда введена некоректно')