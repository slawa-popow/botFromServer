

from spamer.SpamMessage import SpamMessage
from spamer.SpamKeeper import SpamKeeper
from spamer.SpamSender import SpamSender
from spamer.SpamTimer import SpamTimer    

class Spamer:
    # utf8mb4
    M: str = f"""👏Поздравляю! <b>Теперь тебе не придётся ждать ответа от менеджера👏.\n 
        Бесплатная доставка по Минску от 10 единиц при первом заказе 😍.\n 
        Сделай заказ в несколько кликов, выбери адрес и время доставки 🚁.
        </b>"""


    def __init__(self, db, bot) -> None:
        # self.db = db
        self.stimer = None
        self.keeper: SpamKeeper = SpamKeeper(db)
        self.sender: SpamSender = SpamSender(bot)
        self.sender.again_callback = self.new_timer
        self.spam_data = {}


    async def new_message(self, spamData: dict, period_time: int) -> None:
        for k, v in spamData.items():
            if k == 0 or v == '': 
                continue
            msg: SpamMessage = SpamMessage(message=v, id=k)
            await self.keeper.set_message(msg, period_time)

    async def new_timer(self):
        if self.sender.is_spam:
            args = await self.keeper.get_spam_data()
            self.stimer: SpamTimer = SpamTimer('VAPEE', self.sender.send_spam, SpamTimer.PERIOD, args)
            

    async def del_all_spam(self):
        await self.keeper.del_all_spam()

            
    async def stopspam(self):
        self.sender.is_spam = False 
        self.stimer = None

    async def get_all_spam(self):
        return await self.keeper.get_spam_data()

    async def add_victim(self):
        # [1941650155, 6627246261]:
        await self.new_message(self.spam_data, SpamTimer.PERIOD)

    
    async def add_victim_id_text(self, idText: list):
        self.spam_data.update([idText])


    async def init(self):
        self.sender.is_spam = True
        await self.new_timer()


    def set_duration_spam(self, value: int):
        v = 0
        try:
            v = int(value)
        except Exception:
            v = 3600
        finally:
            SpamTimer.PERIOD = v


    def get_duration(self) -> int:
        return SpamTimer.PERIOD

    