from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import Config
from database.db import DataBase
from database.basket import Basket
from states.fsm_states import Order
from keyboards.keyboards import *
from utils import *
from middlewares.AuthFilter import AuthFilter
from datetime import datetime
from spamer.Spamer import Spamer

STOP_INPUT = 'noid'

bot = Bot(token=Config.TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
db = DataBase()
dp.setup_middleware(AuthFilter(db))
basket = Basket(db)
spamer = Spamer(db, bot)

def get_items_basket(result) -> str:
    llist = []
    for x in result:
        llist.append(x[16]*x[14])
    sdfsdf =sum([float(i) for i in llist])
    return '\n'.join([f'{index+1}) {el[11]} {el[14]} шт по {el[16]} = {el[16]*el[14]}  руб' for index, el in enumerate(result)]) + f"\n\n<b>итого: {sdfsdf} руб</b>"



# Стартовая функция
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    
    await Order.start.set()
    user_id = str(message.from_user.id)
    user_name = message.from_user.username
    await state.update_data(usrid=user_id, chatID=message.chat.id, user_name=f'@{user_name}')
    current_datetime = str(datetime.now())
    tmpd = {
        'uid': user_id,
        'user_name': user_name,
        'date': current_datetime
    }
    await basket.create_basket_table(user_id=user_id)
    await message.answer(
        """ 👏Поздравляю! Теперь тебе не придётся ждать ответа от менеджера👏.\n Бесплатная доставка по Минску от 10 единиц при первом заказе 😍.\n Сделай заказ в несколько кликов, выбери адрес и время доставки 🚁.\nЖми 'поиск/заказать'\n\n\n<b>Видео инструкция находится в стадии записи.....</b>""",
        reply_markup=get_kb_main(user_id)
    )
    # await bot.send_video(message.chat.id, open('/home/media/bandicam.mp4', 'rb'))
    return await basket.run_sesion_timer({
        'id': user_id, 
        'time_session': Config.TIME_SESSION,
        'callback': basket.clb_delete_session,
        'args': (message, tmpd)
    })  


@dp.message_handler(state=Order.auth)
async def enter_pswd(message: types.Message, state: FSMContext):
    passw = message.text
    await message.delete()
    await message.answer(f"{'*' * len(passw)}")
    hash_passw = encode_password(passw)
    await state.update_data(token=hash_passw)
    await state.reset_state(with_data = False)
    await message.answer('Хорошо.\nВведи команду еще раз.')
     

@dp.message_handler(commands=['stopSpam'], state='*')
async def safe_spam_stop(message: types.Message, state: FSMContext):
    await message.answer('Хватит спамить.')
    await spamer.stopspam()  


@dp.message_handler(commands=['info'], state='*')
async def safe_info(message: types.Message, state: FSMContext):
    await message.answer(f"""<b>Служебные команды:</b>\n
    <i>/startSpam</i>   --  Начать маркетинг
    <i>/stopSpam</i>    --   Закончить маркетинг
    <i>/periodSpam</i>  --  Значение интервала заданного для процедуры маркетинга
    <i>/clearSpam</i>   --  Удалить все маркетинги из бд
    <i>/allSpam</i>     --  Показать весь маркетинг
    
    """)
    


@dp.message_handler(commands=['startSpam'], state='*')
async def safe_spam_start(message: types.Message, state: FSMContext):
    await message.answer('Погнали спамить....')
    await message.answer('Введи число (секундов) интервала между спамов:')
    await Order.duration_spam.set()


@dp.message_handler(commands=['clearSpam'], state='*')
async def safe_spam_clear(message: types.Message, state: FSMContext):
    await message.answer('Очистить все спам-сообщения.')
    await spamer.del_all_spam()
    await message.answer('Очищено')
    return await spamer.stopspam()


@dp.message_handler(commands=['allSpam'], state='*')
async def safe_spam_all_get(message: types.Message, state: FSMContext):
    await message.answer('Весь спам:')
    all_spam = await spamer.get_all_spam()
    for row in all_spam:
        id, txt, dur = row[1:]
        await message.answer(f'{id}: {txt}\n-------------------------\nпериод: {dur} сек')
     
     
    
    

@dp.message_handler(state=Order.duration_spam)
async def safe_spam_input_id(message: types.Message, state: FSMContext):
    input = message.text
    spamer.set_duration_spam(input)
    dur = spamer.get_duration()
    await Order.victim.set()
    await message.answer(f'Задано: {dur} сек')
    
    return await message.answer('Введи айди группы в которую надо спамить.\nЧтобы продолжить без ввода или закончить ввод id набери <b>noid</b>')


@dp.message_handler(state=Order.victim)
async def safe_add_victim(message: types.Message, state: FSMContext):
    # [1941650155, 6627246261]
    input = message.text
    if input.strip() == STOP_INPUT:
        await state.reset_state(with_data = False)
        await spamer.add_victim()
        await spamer.init()
        return await message.answer('Закончили ввод id.')
    try:
        input = int(message.text)
    except Exception:
        await message.answer('Введено не число')
    else:
        await state.update_data(spamid=input)
        await Order.victim_text.set()
        
        return await message.answer('Введи текст спама:')
    
    
@dp.message_handler(state=Order.victim_text)
async def safe_add_victim_text(message: types.Message, state: FSMContext):
    input = message.text
    if input == STOP_INPUT:
        await state.reset_state(with_data = False)
        await spamer.add_victim()
        await spamer.init()
        return await message.answer('Закончили ввод text.')
    else:
        _id = await state.get_data()
        id = _id.get('spamid', "")
        await spamer.add_victim_id_text([id, input])
        await Order.victim.set()
        return await message.answer('Введи айди группы в которую надо спамить.\nЧтобы закончить ввод набери <b>noid</b>')
    
        
@dp.message_handler(commands=['periodSpam'], state='*')
async def safe_spam_period(message: types.Message, state: FSMContext):
    dur = spamer.get_duration()
    await message.answer(f'Интервал спама: {dur} секунд')
    

# Здесь бот завершает процесс заказа, пользователь нажал завершить
@dp.callback_query_handler(lambda m: m.data and m.data == 'exit_order', state=Order.all_states_names)
async def exit_order_callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await db.delete_basket_table(user_id=user_id)
    if user_id in basket.basket_table:
        basket.basket_table.remove(user_id)
        basket.curr_timers.pop(user_id)
    await callback_query.message.answer('Выход из процесса заказа, корзина очищена. Нажмите /start для начала.')
    await state.finish()


@dp.message_handler(text='завершить', state=Order.change_order)
async def exit_order_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await db.delete_basket_table(user_id=user_id)
    if user_id in basket.basket_table:
        basket.basket_table.remove(user_id)
        basket.curr_timers.pop(user_id)
    await message.answer('Выход из процесса заказа, корзина очищена. Нажмите /start для начала.')
    await state.finish()


# Задать вопрос менеджеру
@dp.message_handler(text='задать вопрос', state=Order.all_states_names)
async def ask_question(message: types.Message, state: FSMContext):
    await message.answer('Чтобы задать вопрос, напишите @Vapee_manager.')


# Здесь бот ловит сообщение от webApp отправленное window.Telegram.WebApp.sendData() из javascript 
@dp.message_handler(lambda msg: msg.web_app_data.data=='order-off', content_types='web_app_data', state=Order.start)
@dp.message_handler(text='корзина', state=Order.start)
async def order_basket(message: types.Message,  state: FSMContext) -> None:
    us = await state.get_data()
    usid = us.get('usrid', '')
    if not usid:
        return await message.answer('Я не знаю ваш id. Напишите /start.')
    result = await basket.get_basket(usid)
    prods = get_items_basket(result)
    kb, inline_kb = get_kb_after_web_app(usid)
    await message.answer('Ваши товары в корзине', reply_markup=kb)
    return await message.answer(f"{prods}", reply_markup=inline_kb)


# Переходим к оформлению заказа
@dp.callback_query_handler(lambda m: m.data and m.data in ('go_to_checkout', 'change_delivery'), state=Order.start)
async def continue_order(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Выберите способ доставки', reply_markup=get_kb_order_delivery())


# Переходим к просмотру способов доставки
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('delivery_'), state=Order.start)
async def select_delivery(callback_query: types.CallbackQuery, state: FSMContext):
    delivery_method = callback_query.data.replace('delivery_', '')
    if delivery_method == 'Самовывоз':
        msg_text = 'Самовывоз\nСтоимость: 0 руб\nСрок отгрузки: сегодня'
        media = types.MediaGroup()
        media.attach_photo(types.InputFile('media/self_pickup/map.jpg'))
        media.attach_photo(types.InputFile('media/self_pickup/photo.jpg'))
        await callback_query.message.answer_media_group(media)
        return await callback_query.message.answer(
            msg_text,
            reply_markup=get_kb_delivery_choice(delivery_method)
        )
    elif delivery_method == 'Доставка по г. Минск':
        msg_text = 'Доставка по г. Минск\nСтоимость:\nот 10 единиц - 7 рублей\nот 30 единиц - 5 рублей\nСроки отгрузки: при оформлении до 16:30 доставка в день оформления'
    elif delivery_method == 'Маршруткой по РБ':
        msg_text = 'Маршруткой по РБ\nСтоимость: 5-10 руб маршрутчику\nСроки отгрузки: доставка на завтра\n100% предоплата'
    elif delivery_method == 'ЯндексДоставка по городу':
        msg_text = 'ЯндексДоставка по городу\nСтоимость: по тарифу Яндекс\nСроки отгрузки: через 10 мин\n100% предоплата'
    else:
        return await callback_query.message.edit_text(
            'Выберите:',
            reply_markup=get_kb_post_rb_delivery()
        )
    await callback_query.message.edit_text(
        msg_text,
        reply_markup=get_kb_delivery_choice(delivery_method)
    )


# Доставка почтой по РБ
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('rb_delivery'), state=Order.start)
async def select_rb_delivery(callback_query: types.CallbackQuery, state: FSMContext):
    delivery_method = callback_query.data.replace('rb_delivery_', '')
    if delivery_method == 'Европочта':
        await callback_query.message.edit_text(
            'Европочта\nСтоимость доставки: # руб\nСроки отгрузки: при оформлении до 16:30 отправка в день оформления\n100% предоплата',
            reply_markup=get_kb_delivery_choice('Европочта')
        )
    elif delivery_method == 'Автолайт':
        await callback_query.message.edit_text(
            'Автолайт (100 единиц)\nСтоимость доставки: # руб\nСроки отгрузки: на следующий день\n100% предоплата',
            reply_markup=get_kb_delivery_choice('Автолайт')
        )


# Выбрали способ доставки
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('selected_delivery'), state=Order.start)
async def shipment_process(callback_query: types.CallbackQuery, state: FSMContext):
    delivery_method = callback_query.data.replace('selected_delivery_', '')
    # запись в бд
    await db.update_delivery_method(user_id=callback_query.from_user.id, delivery_method=delivery_method)
    await state.update_data(delivery_method=delivery_method)
    if delivery_method == 'Самовывоз':
        await Order.delivery_date.set()
        await callback_query.message.edit_text(
            'Выберите дату доставки (при самовывозе дату самовывоза), до 15:30 МСК доступна сегодня',
            reply_markup=get_kb_delivery_date(is_today_delivery())
        )
    else:
        await Order.delivery_address.set()
        await callback_query.message.edit_text('Укажите полный адрес доставки')


# Пользователь указал адрес доставки
@dp.message_handler(state=Order.delivery_address)
async def get_delivery_address(message: types.Message, state: FSMContext):
    await state.update_data(delivery_address=message.text)
    await db.update_delivery_address(user_id=message.from_user.id, delivery_address=message.text)
    data = await state.get_data()
    delivery_method = data.get('delivery_method')
    if delivery_method == 'ЯндексДоставка по городу':
        await Order.start.set()
        return await message.answer(
            'Хорошо, отправим в ближайшее рабочее время.',
            reply_markup=get_kb_yandex_delivery()
        )
    await Order.next()
    await message.answer(
        'Выберите дату доставки (при самовывозе дату самовывоза), до 15:30 МСК доступна сегодня',
        reply_markup=get_kb_delivery_date(is_today_delivery())
    )
    

# Выбираем время доставки
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('date_delivery'), state=Order.delivery_date)
async def get_shipment_date(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.next()
    delivery_date = callback_query.data.replace('date_delivery_', '')
    await state.update_data(delivery_date=delivery_date)
    await callback_query.message.edit_text(
        'Укажите время доставки/самовывоза',
        reply_markup=get_kb_delivery_time()
    )


# Предварительный просмотр заказа

# после яндекс доставки пропускает выбор дня и времени
@dp.callback_query_handler(text='confirm_yandex_delivery', state=Order.start)

@dp.callback_query_handler(lambda m: m.data and m.data.startswith('time_delivery'), state=Order.delivery_time)
async def get_shipment_time(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    delivery_time = callback_query.data.replace('time_delivery_', '')
    await state.update_data(delivery_time=delivery_time)
    usid = data.get('usrid')
    result = await basket.get_basket(usid)
    prods = get_items_basket(result)
    delivery_method = data.get('delivery_method')
    delivery_address = data.get('delivery_address') if delivery_method != 'Самовывоз' else 'Самовывоз'
    delivery_date = data.get('delivery_date')
    # запись в бд
    msg_text = f'Проверьте всё ли верно:\n\nВы заказали: {prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        await db.update_datetime_delivery(user_id=callback_query.from_user.id, delivery_datetime=f'{delivery_time} {delivery_date}')
        yandex_delivery = False
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        await db.update_datetime_delivery(user_id=callback_query.from_user.id, delivery_datetime='ЯндексДостака')
        yandex_delivery = True
        msg_text += f'Отправление в ближайшее время'
    await callback_query.message.edit_text(
        msg_text,
        reply_markup=get_kb_payment_proceeding(yandex_delivery)
    )


# Изменение состава заказа
@dp.callback_query_handler(text='change_order', state=Order.all_states_names)
async def select_pay_method(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.change_order.set()
    data = await state.get_data()
    usid = data.get('usrid')
    await callback_query.message.answer(
        'Измените заказ, нажав на кнопку ниже',
        reply_markup=get_kb_change_order(usid)
    )


# Возврат из веб-приложения к боту во время изменения заказа
@dp.message_handler(lambda msg: msg.web_app_data.data=='order-off', content_types='web_app_data', state=Order.change_order)
async def change_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    usid = data.get('usrid', '')
    if not usid:
        return await message.answer('Я не знаю ваш id. Напишите /start.')
    result = await basket.get_basket(usid)
    prods = get_items_basket(result)
    delivery_method = data.get('delivery_method')
    is_self_pickup = True if data.get('delivery_method') == 'Самовывоз' else False
    delivery_address = data.get('delivery_address') if delivery_method != 'Самовывоз' else 'Самовывоз'
    delivery_date = data.get('delivery_date')
    delivery_time = data.get('delivery_time')
    msg_text = f'Проверьте всё ли верно:\n\nВы заказали: {prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        yandex_delivery = False
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        yandex_delivery = True
        msg_text += f'Отправление в ближайшее время'
    await message.answer(
        msg_text,
        reply_markup=get_kb_change('items', yandex_delivery, is_self_pickup)
    )


# Изменение адреса доставки
@dp.callback_query_handler(text='change_delivery_address', state=Order.all_states_names)
async def change_delivery_address(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.change_delivery_address.set()
    await callback_query.message.edit_text('Укажите полный адрес доставки')
    

@dp.message_handler(state=Order.change_delivery_address)
async def set_new_delivery_address(message: types.Message, state: FSMContext):
    delivery_address = message.text
    await state.update_data(delivery_address=delivery_address)
    await db.update_delivery_address(user_id=message.from_user.id, delivery_address=delivery_address)
    data = await state.get_data()
    usid = data.get('usrid', '')
    if not usid:
        return await message.answer('Я не знаю ваш id. Напишите /start.')
    result = await basket.get_basket(usid)
    prods = get_items_basket(prods)
    delivery_method = data.get('delivery_method')
    delivery_date = data.get('delivery_date')
    delivery_time = data.get('delivery_time')
    msg_text = f'Проверьте всё ли верно:\n\nВы заказали: {prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        yandex_delivery = False
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        yandex_delivery = True
        msg_text += f'Отправление в ближайшее время'
    await message.answer(
        msg_text,
        reply_markup=get_kb_change('address', yandex_delivery)
    )


# Изменение даты доставки
@dp.callback_query_handler(text='change_delivery_datetime', state=Order.all_states_names)
async def change_delivery_datetime(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.change_delivery_date.set()
    await callback_query.message.edit_text(
        'Выберите дату доставки (при самовывозе дату самовывоза), до 15:30 МСК доступна сегодня',
        reply_markup=get_kb_delivery_date(is_today_delivery())
    )


# Изменение времени доставки
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('date_delivery'), state=Order.change_delivery_date)
async def change_delivery_date(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.change_delivery_time.set()
    delivery_date = callback_query.data.replace('date_delivery_', '')
    await state.update_data(delivery_date=delivery_date)
    await callback_query.message.edit_text(
        'Укажите время доставки/самовывоза',
        reply_markup=get_kb_delivery_time()
    )


@dp.callback_query_handler(lambda m: m.data and m.data.startswith('time_delivery'), state=Order.change_delivery_time)
async def change_delivery_date(callback_query: types.CallbackQuery, state: FSMContext):
    delivery_time = callback_query.data.replace('time_delivery_', '')
    await state.update_data(delivery_time=delivery_time)
    data = await state.get_data()
    is_self_pickup = True if data.get('delivery_method') == 'Самовывоз' else False
    result = await basket.get_basket(callback_query.from_user.id)
    prods = get_items_basket(result)
    delivery_method = data.get('delivery_method')
    delivery_date = data.get('delivery_date')
    delivery_address = data.get('delivery_address') if delivery_method != 'Самовывоз' else 'Самовывоз'
    msg_text = f'Проверьте всё ли верно:\n\nВы заказали: {prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        await db.update_datetime_delivery(user_id=callback_query.from_user.id, delivery_datetime=f'{delivery_time} {delivery_date}')
        yandex_delivery = False
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        await db.update_datetime_delivery(user_id=callback_query.from_user.id, delivery_datetime='ЯндексДостака')
        yandex_delivery = True
        msg_text += f'Отправление в ближайшее время'
    await callback_query.message.edit_text(
        msg_text,
        reply_markup=get_kb_change('datetime', yandex_delivery, is_self_pickup)
    )


# Получение комментария
@dp.callback_query_handler(text='write_comment', state=Order.all_states_names)
async def get_comment(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.comment.set()
    await callback_query.message.edit_text(
        'Оставить комментарий?',
        reply_markup=get_kb_comment()
    )


@dp.callback_query_handler(text='select_comment', state=Order.comment)
async def get_comment(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('Укажите комментарий')


@dp.message_handler(state=Order.comment)
async def get_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await db.update_comment(user_id=message.from_user.id, comment=message.text)
    await message.answer(
        'Выберите: ',
        reply_markup=get_kb_after_comment()
    )


# Выбор метода оплаты
@dp.callback_query_handler(text='select_pay_method', state=Order.all_states_names)
async def select_pay_method(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('comment'):
        await db.update_comment(user_id=callback_query.from_user.id, comment='NO') 
    await Order.payment_method.set()
    data = await state.get_data()
    only_online_payment = False if data.get('delivery_method') in ('Самовывоз', 'Доставка по г. Минск') else True
    await callback_query.message.edit_text(
        'Способы оплаты: ',
        reply_markup=get_kb_payment_methods(only_online_payment)
    )


@dp.callback_query_handler(lambda m: m.data and m.data.startswith('pay_method'), state=Order.payment_method)
async def payment_proceeding(callback_query: types.CallbackQuery, state: FSMContext):
    payment_method = callback_query.data.replace('pay_method_', '')
    if payment_method == 'Безналичный расчет':
        await callback_query.message.edit_text(
            'Выбор банка: ',
            reply_markup=get_kb_banks()
        )
    else:
        await db.update_pay_method(user_id=callback_query.from_user.id, pay_method=payment_method)
        await state.update_data(pay_method=payment_method)
        await callback_query.message.edit_text(
            'Подтвердите заказ',
            reply_markup=get_kb_confirm_order()
        )


# Выбор банка безналичной оплаты
@dp.callback_query_handler(lambda m: m.data and m.data.startswith('bank'), state=Order.payment_method)
async def select_bank(callback_query: types.CallbackQuery, state: FSMContext):
    bank_name = callback_query.data.replace('bank_', '')
    await db.update_pay_method(user_id=callback_query.from_user.id, pay_method=bank_name)
    if bank_name == 'БНБ банк':
        await Order.bank_choice.set()
        await callback_query.message.edit_text(
            'Реквизиты для пополнения через ерип: 3001899330002523/9969\n' + \
            'Заходите в древо ерип\n' + \
            '- Банковские финансовые системы\n' + \
            '- Банки нкфо\n' + \
            '- БНБ банк\n' + \
            '- Пополнение карты\n' + \
            'Вводите счёт, пополняете.',
            reply_markup=get_kb_after_banks()
        )
    else:
        await callback_query.message.edit_text(
            'Подтвердите заказ',
            reply_markup=get_kb_confirm_order()
        )


# Получение чека от пользователя
@dp.callback_query_handler(text='go_to_receipt', state=Order.bank_choice)
async def go_to_receipt(callback_query: types.CallbackQuery, state: FSMContext):
    await Order.payment_receipt.set()   
    await callback_query.message.answer(
        'Отправьте ответным сообщением чек с оплатой',
        reply_markup=get_kb_receipt()
    )


@dp.message_handler(state=Order.payment_receipt, content_types='photo')
async def go_to_receipt(message: types.Message, state: FSMContext):
    for photo in message.photo[::-1]:
        # меньше или равно 1 мб
        if photo.file_size <= 1024*1024:
            file_id = photo.file_id
            break
    else:
        return await message.answer(
            'Отправьте другое фото!',
            reply_markup=get_kb_receipt()
        )
    result = (await bot.download_file_by_id(file_id)).getvalue()
    await state.update_data(receipt=result)
    await state.update_data(pay_method='БНБ банк')
    await db.update_receipt(user_id=message.from_user.id, photo=result)
    await db.update_pay_status(user_id=message.from_user.id, status='Оплачено')
    await db.update_pay_method(user_id=message.from_user.id, pay_method='БНБ банк')
    await message.answer(
        'Хорошо, обработано!',
        reply_markup=get_kb_confirm_order()
    )


@dp.message_handler(state=Order.payment_receipt, content_types=NOT_ALLOWED_CONTENT_TYPES_RECEIPT)
async def go_to_receipt(message: types.Message, state: FSMContext):
    await message.answer(
        'Отправьте картинку!',
        reply_markup=get_kb_receipt()
    )


# Вернуться в состояние выбора метода оплаты
@dp.callback_query_handler(text='go_to_order', state=Order.payment_method)
async def go_to_order(callback_query: types.CallbackQuery, state: FSMContext):
    result = await basket.get_basket(callback_query.from_user.id)
    prods = get_items_basket(result)
    data = await state.get_data()
    is_self_pickup = True if data.get('delivery_method') == 'Самовывоз' else False
    delivery_method = data.get('delivery_method')
    delivery_date = data.get('delivery_date')
    delivery_address = data.get('delivery_address') if delivery_method != 'Самовывоз' else 'Самовывоз'
    delivery_time = data.get('delivery_time')
    msg_text = f'Проверьте всё ли верно:\n\nВы заказали: {prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        yandex_delivery = False
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        yandex_delivery = True
        msg_text += f'Отправление в ближайшее время'
    await callback_query.message.edit_text(
        msg_text,
        reply_markup=get_kb_change('before_payment', yandex_delivery, is_self_pickup)
    )


# Подтверждение заказа
@dp.callback_query_handler(text='confirm_order', state=Order.all_states)
async def confirm_order(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    user_name = data.get('user_name')
    if user_name is not None:
        await db.update_user_name(user_id=user_id, user_name=f'@{user_name}')
    else:
        await Order.no_username.set()
        return await callback_query.message.edit_text(
            'Мне не удалось определить твой @username (тег) в телеграм. Пожалуйста, сообщи как с тобой связаться (отправь произвольное сообщение, текстом)'
        )

    result = await basket.get_basket(user_id)
    receipt = data.get('receipt')
    prods = get_items_basket(result)
    delivery_method = data.get('delivery_method')
    delivery_date = data.get('delivery_date')
    delivery_address = data.get('delivery_address') if delivery_method != 'Самовывоз' else 'Самовывоз'
    delivery_time = data.get('delivery_time')
    comment = data.get('comment', 'Без комментария')
    pay_method = data.get('pay_method')
    msg_text = f'Вы заказали:\n{prods}\nСпособ доставки: {delivery_method}\nАдрес: {delivery_address}\n'
    if delivery_method != 'ЯндексДоставка по городу':
        msg_text += f'Дата и время: {delivery_time} {delivery_date}'
    else:
        msg_text += f'Отправление в ближайшее время'
    msg_text += f'\nКомментарий: {comment}'
    msg_text += f'\nСпособ оплаты: {pay_method}'

    await db.update_order_status(user_id=user_id, status='В ожидании')
    await db.transfer_basket_to_orders(user_id=user_id, data=result)
    await state.finish()
    await db.delete_basket_table(user_id=user_id)
    if user_id in basket.basket_table:
        basket.basket_table.remove(user_id)
        basket.curr_timers.pop(user_id)
    await callback_query.message.edit_text(
        msg_text
    )
    await callback_query.message.answer(
        'Благодарю за заказ! Передадим как договаривались :)',
        reply_markup=types.ReplyKeyboardRemove()
)
    # 
    # ------------- айди менеджера сменить на сущв-й ----------------------------------------
    #
    admin_id = "66272XXXXX"
    await bot.send_message(chat_id=admin_id, text=f'{user_name} сделал заказ.\n\n{msg_text}')
    if receipt:
        await bot.send_photo(chat_id=admin_id, photo=receipt, caption='Чек оплаты')


@dp.message_handler(state=Order.no_username)
async def get_user_contacts(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(user_name=message.text)
    await db.update_user_name(user_id=user_id, user_name=message.text)
    await message.answer(
        'Хорошо, спасибо',
        reply_markup=get_kb_confirm_order()
    )


if __name__ == '__main__':
    print('\n--------- start bot ---------\n')
    executor.start_polling(dp)