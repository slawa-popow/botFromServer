from aiogram.dispatcher.filters.state import State, StatesGroup


class Order(StatesGroup):
    """
    start - выбор товара, просмотр вариантов доставки
    delivery_address - ввод адреса доставки
    comment - комментарий
    delivery_date - дата доставки
    delivery_time - время доставки
    change_order - изменение состава заказа
    change_delivery_address - изменение адреса доставки
    change_delivery_time - изменение времени доставки
    payment_method - метод оплаты
    """
    start = State()
    delivery_address = State()
    delivery_date = State()
    delivery_time = State()
    change_order = State()
    change_delivery_address = State()
    change_delivery_date = State()
    change_delivery_time = State()
    comment = State()
    payment_method = State()
    bank_choice = State()
    payment_receipt = State()
    no_username = State()

    auth = State()
    duration_spam = State()
    victim = State() 
    victim_text = State()
    