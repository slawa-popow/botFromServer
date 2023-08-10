import aiogram.types as types
from aiogram.types import WebAppInfo
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


def get_kb_main(user_id) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('поиск/заказать', web_app=WebAppInfo(url=f'https://web-app-bot-b.vercel.app/?usid=User_{user_id}')))
    kb.row(KeyboardButton('задать вопрос'))
    return kb


def get_kb_after_web_app(user_id) -> (ReplyKeyboardMarkup, InlineKeyboardMarkup):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('выбор товара', web_app=WebAppInfo(url=f'https://web-app-bot-b.vercel.app/?usid=User_{user_id}')))
    kb.add(KeyboardButton('корзина'))
    kb.row(KeyboardButton('задать вопрос'))

    inline_kb = InlineKeyboardMarkup()
    inline_kb.row(InlineKeyboardButton('перейти к оформлению', callback_data='go_to_checkout'))
    inline_kb.row(InlineKeyboardButton('завершить', callback_data='exit_order'))
    return kb, inline_kb


def get_kb_order_delivery(pre='delivery_') -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.row(InlineKeyboardButton('самовывоз', callback_data=f'{pre}Самовывоз'))
    inline_kb.row(InlineKeyboardButton('доставка по г. Минск', callback_data=f'{pre}Доставка по г. Минск'))
    inline_kb.row(InlineKeyboardButton('доставка почтой по РБ', callback_data=f'{pre}Доставка почтой по РБ'))
    inline_kb.row(InlineKeyboardButton('ЯндексДоставка по городу', callback_data=f'{pre}ЯндексДоставка по городу'))
    inline_kb.row(InlineKeyboardButton('маршруткой по РБ', callback_data=f'{pre}Маршруткой по РБ'))
    return inline_kb


def get_kb_delivery_choice(delivery_name) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.row(InlineKeyboardButton('ок, продолжить', callback_data=f'selected_delivery_{delivery_name}'))
    inline_kb.row(InlineKeyboardButton('изменить способ доставки', callback_data='change_delivery'))
    return inline_kb


def get_kb_post_rb_delivery(pre='rb_delivery_') -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.row(InlineKeyboardButton('Европочта', callback_data=f'{pre}Европочта'))
    inline_kb.row(InlineKeyboardButton('Автолайт (100 единиц)', callback_data=f'{pre}Автолайт'))
    inline_kb.row(InlineKeyboardButton('изменить способ доставки', callback_data='change_delivery'))
    return inline_kb


def get_kb_delivery_date(today: bool, pre='date_delivery_') -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    if today:
        inline_kb.add(InlineKeyboardButton('Сегодня', callback_data=f'{pre}сегодня'))
    inline_kb.add(InlineKeyboardButton('Завтра', callback_data=f'{pre}завтра'))
    inline_kb.add(InlineKeyboardButton('Послезавтра', callback_data=f'{pre}послезавтра'))
    return inline_kb


def get_kb_delivery_time(pre='time_delivery_') -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('с 16:00 до 18:00', callback_data=f'{pre}16:00-18:00'))
    inline_kb.add(InlineKeyboardButton('с 18:00 до 20:00', callback_data=f'{pre}18:00-20:00'))
    inline_kb.add(InlineKeyboardButton('с 20:00 до 22:00', callback_data=f'{pre}20:00-22:00'))
    return inline_kb


def get_kb_payment_proceeding(yandex_delivery: bool) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Продолжить', callback_data='write_comment'))
    # inline_kb.add(InlineKeyboardButton('Верно, к выбору способа оплаты', callback_data='select_pay_method'))
    inline_kb.add(InlineKeyboardButton('Изменить заказ', callback_data='change_order'))
    inline_kb.add(InlineKeyboardButton('Изменить адрес', callback_data='change_delivery_address'))
    if not yandex_delivery:
        inline_kb.add(InlineKeyboardButton('Изменить дату и время доставки', callback_data='change_delivery_datetime'))
    inline_kb.add(InlineKeyboardButton('Завершить', callback_data='exit_order'))
    return inline_kb


def get_kb_change_order(user_id: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton('выбор товара', web_app=WebAppInfo(url=f'https://web-app-bot-b.vercel.app/?usid=User_{user_id}')))
    kb.row(KeyboardButton('завершить'))
    return kb


def get_kb_change(change_option: str, is_yandex_delivery: bool, is_self_pickup: bool=False) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Продолжить', callback_data='write_comment'))
    if change_option == 'items':
        if not is_self_pickup:
            inline_kb.add(InlineKeyboardButton('Изменить адрес', callback_data='change_delivery_address'))
        if not is_yandex_delivery:
            inline_kb.add(InlineKeyboardButton('Изменить дату и время/самовывоза', callback_data='change_delivery_datetime'))
    elif change_option == 'address':
        inline_kb.add(InlineKeyboardButton('Изменить заказ', callback_data='change_order'))
        if not is_yandex_delivery:
            inline_kb.add(InlineKeyboardButton('Изменить дату и время доставки/самовывоза', callback_data='change_delivery_datetime'))
    elif change_option == 'datetime':
        inline_kb.add(InlineKeyboardButton('Изменить заказ', callback_data='change_order'))
        if not is_self_pickup:
            inline_kb.add(InlineKeyboardButton('Изменить адрес', callback_data='change_delivery_address'))
    else:
        inline_kb.add(InlineKeyboardButton('Изменить заказ', callback_data='change_order'))
        if not is_self_pickup:
            inline_kb.add(InlineKeyboardButton('Изменить адрес', callback_data='change_delivery_address'))
        if not is_yandex_delivery:
            inline_kb.add(InlineKeyboardButton('Изменить дату и время доставки/самовывоза', callback_data='change_delivery_datetime'))
    inline_kb.add(InlineKeyboardButton('Завершить', callback_data='exit_order'))
    return inline_kb


def get_kb_payment_methods(only_online_payment: bool, pre='pay_method_') -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    if not only_online_payment:
        inline_kb.add(InlineKeyboardButton('Самовывоз', callback_data=f'{pre}Самовывоз'))
        inline_kb.add(InlineKeyboardButton('Курьеру при получении', callback_data=f'{pre}Курьеру при получении'))
    inline_kb.add(InlineKeyboardButton('Безналичный расчет', callback_data=f'{pre}Безналичный расчет'))
    inline_kb.add(InlineKeyboardButton('Вернуться назад', callback_data=f'go_to_order'))
    return inline_kb


def get_kb_banks() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('БНБ банк', callback_data='bank_БНБ банк'))
    # inline_kb.add(InlineKeyboardButton('yoomoney', callback_data='bank_yoomoney'))
    inline_kb.add(InlineKeyboardButton('Изменить способ оплаты', callback_data='select_pay_method'))
    return inline_kb


def get_kb_after_banks() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Ок, продолжить', callback_data='go_to_receipt'))
    inline_kb.add(InlineKeyboardButton('Изменить способ оплаты', callback_data='select_pay_method'))
    return inline_kb


def get_kb_confirm_order() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Подтвердить заказ', callback_data='confirm_order'))
    inline_kb.add(InlineKeyboardButton('Изменить способ оплаты', callback_data='select_pay_method'))
    return inline_kb


def get_kb_yandex_delivery() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Продолжить', callback_data='confirm_yandex_delivery'))
    inline_kb.add(InlineKeyboardButton('Вернуться назад', callback_data='go_to_checkout'))
    return inline_kb


def get_kb_comment() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Указать комментарий', callback_data='select_comment'))
    inline_kb.add(InlineKeyboardButton('Продолжить без комментария', callback_data='select_pay_method'))
    inline_kb.add(InlineKeyboardButton('Вернуться назад', callback_data='go_to_order'))
    return inline_kb


def get_kb_after_comment() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('К выбору способа оплаты', callback_data='select_pay_method'))
    inline_kb.add(InlineKeyboardButton('Вернуться назад', callback_data='write_comment'))
    return inline_kb


def get_kb_receipt() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('Вернуться назад', callback_data='select_pay_method'))
    return inline_kb