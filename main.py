import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import EnvData
from handlers import user_handlers, tariff_handlers, other_handlers, moder_handlers

# Инициализируем логгер
logger = logging.getLogger(__name__)
bot = Bot(token=EnvData.bot_token, parse_mode='HTML')


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    # логи пишутся в файл logs.log +1 балл за работу с файлами
    logging.basicConfig(
        # filename='logs.log',
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Инициализируем бот и диспетчер
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(tariff_handlers.router)
    dp.include_router(moder_handlers.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# запускаем работу бота
if __name__ == '__main__':
    asyncio.run(main())
