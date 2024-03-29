from aiogram.filters.callback_data import CallbackData


class HasTariffCallbackFactory(CallbackData, prefix='has_tariff'):
    tariff_name: str
    frequency: int | str
    duration: int | str


class ChangeTariffCallbackFactory(CallbackData, prefix='change_tariff'):
    name: str
    price: int | str
