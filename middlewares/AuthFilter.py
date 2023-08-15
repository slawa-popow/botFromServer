
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from states.fsm_states import Order

class AuthFilter(BaseMiddleware):

    def __init__(self, db):
        super().__init__()
        self.db = db

    async def _get_pswd(self, id):
        result = await self.db.get_admin_auth(id=id)
         
        if isinstance(result, (list, tuple)) and len(result) > 0:
            return result[0][2]
        return None
    

    async def on_process_message(self, message: types.Message, data: dict):
        # 7673
        # Get current handler
        handler = current_handler.get()
        is_safe: bool = handler.__name__.startswith('safe_', )
        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        state = dispatcher.current_state()

        if is_safe:
            password = await self._get_pswd(message.from_user.id)
            _token = await state.get_data()
            token = _token.get('token')
            if (not password) or (not token) or (password != token):
                await message.answer(f'Доступ запрещен. Введи пароль:') 
                await state.set_state(Order.auth)
                # Cancel current handler
                raise CancelHandler()
            
                
        # print('state: ', state.storage.__dict__)
        # print('message: ', message.__dict__)
        # print('handler: ', is_safe)
       
      
       
         
