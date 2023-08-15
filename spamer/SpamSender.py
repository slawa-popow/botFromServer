
from typing import Callable

class SpamSender:

    def __init__(self, bot) -> None:
        self.bot = bot
        self.again_callback: Callable = None
        self.is_spam: bool = True
        self.counter = 1


    async def send_spam(self, *args, **kwargs):
        """
            args[2] - message text
            args[1] - id group
        """
        
        for a in args:
            id_group = a[1]
            message = a[2]
            await self.bot.send_message(id_group, message + f'\n[{self.counter}]')
            print('message sended ', id_group, message, sep='\n')
        if self.is_spam and self.again_callback and isinstance(self.again_callback, Callable):
            await self.again_callback()
            print('again timer start', self.counter)
            self.counter += 1
