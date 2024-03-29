from dataclasses import dataclass
from environs import Env
import json
from db.models import session, Tariff




class TariffInfo:

    frequency = [1, 2, 4, 6, 8, 12, 24]
    # tariffs = {
    #     'Кэшбэк': 0,
    #     'Кэшбэк +': 5,
    #     'Товар': 10,
    #     "Услуги МП": 50,
    #     "Реклама": 500
    # }

    @classmethod
    def get_tariffs(self) -> dict:
        queryset = session.query(Tariff).all()
        tariffs = {
            tariff.name: tariff.post_price for tariff in queryset
        }
        return tariffs



class EnvData:
    env = Env()
    env.read_env()
    yootoken = env('YOOTOKEN')
    bot_token = env('BOT_TOKEN')
    moders = json.loads(env('MODER_ID'))
    owners = json.loads(env('OWNER_ID'))
    main_chats = json.loads(env('CHAT_IDS'))