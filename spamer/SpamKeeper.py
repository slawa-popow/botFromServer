from spamer.SpamMessage import SpamMessage


class SpamKeeper:

    def __init__(self, db) -> None:
        self.db = db


    
    async def set_message(self, msg: SpamMessage, period_time: int) -> None:
        await self.db.set_message(table_name='Spam', msg=str(msg), id_group=msg.id, period=period_time)
        
    
    async def get_spam_data(self):
        result = await self.db.get_spam_table_data(table_name='Spam')
        return result
    
    async def del_all_spam(self):
        await self.db.delete_all_spam(table_name='Spam')

    