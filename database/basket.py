from typing import Callable
from .db import DataBase
from aio_timers import Timer
from aiogram import types


class Basket:
    """Корзина"""
    def __init__(self, db: DataBase) -> None:
        self.db: DataBase = db
        self.curr_timers: dict = {}
        self.basket_table: list = []


    async def run_sesion_timer(self, params: dict = None):
        """
        params = {
            id: id_tg:uniq_token
            time_session: int,
            callback: Callable,
            args: *args
        }
        """
        try:
            timer = None
            if params:
                id = params.get('id')
                time_sesion = int(params.get('time_session'))
                callback = params.get('callback')
                args = params.get('args', tuple())
                if id and (isinstance(callback, Callable)) and len(args) > 0:
                    timer = Timer(time_sesion, callback, callback_args=args, callback_async=True)
                    if not self.curr_timers.get(id):
                        self.curr_timers[id] = timer
                else:
                    raise Exception('\nmethod: run_session_timer =>\n---error arguments\n')
        except Exception as e:
            print(e)
        else:
            if timer:
                await timer.wait()


    async def clb_delete_session(self, *args):
        try:
            message, tmpd = args
            usid: str = tmpd.get('uid')
            if not usid:
                raise Exception('\nНе получил telegram_user_id в basket->clb_delete_session()\n')
            await self.db.delete_basket_table(user_id=usid)
            self.basket_table.remove(usid)
            msgtext: str = f"Уважаемый {tmpd.get('uname', 'anonumous')}\nВаша корзина очищена. Сделайте новый заказ, нажав /start.\n{tmpd.get('date', '__:__')}\n"
            return await message.answer(msgtext)
        except Exception as e:
            print(f'\nError in  basket->clb_delete_session() {e}\n')

    
    async def create_basket_table(self, user_id: str):
        """Создать временную таблицу корзины заказа.
            Таблица будет названа значением User_telegram_user_id"""
        try:
            await self.db.create_basket_table(user_id=user_id)
            self.basket_table.append(user_id)
        except Exception as e:
            print(f'error in basket->create_basket_table()\n{e}\n')
        
            
    async def get_basket(self, usid) -> list:
        try:
            result = await self.db.get_basket(table_name=f'User_{usid}')
            return result
        except Exception as e:
            print(f'error in basket->get_basket()\n{e}\n')