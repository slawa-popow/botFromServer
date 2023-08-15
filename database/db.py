from config import Config
from mysql.connector import connect, Error
from functools import wraps
import base64


"""
CREATE TABLE `e110kw29_kitopt`.`cart` ( `id` INT NOT NULL AUTO_INCREMENT , `good` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL , `count` INT NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
ALTER TABLE `userSession` ADD FOREIGN KEY (`cart`) REFERENCES `cart`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
"""


def cdb(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            with connect(
            host=Config.HOST,
            user=Config.USER,
            password=Config.PASSWORD,
            database=Config.DATABASE,
        ) as connection:
                with connection.cursor() as cursor:
                    result = await method(self, cursor, *args, **kwargs)
                    connection.commit()
                    
                    return result
        except Error as e:
            print(e)
    return wrapper


class DataBase:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_sql_basket(cls, table_name: str) -> str:
        sql = f'SELECT * FROM {table_name};'
        return sql
    
    @classmethod
    def create_spam_table(cls, table_name: str) -> str:
        # table name -- Spam
        sql: str = f"""
                    CREATE TABLE IF NOT EXISTS e110kw29_kitopt.{table_name} ( 
                        `id` INT NOT NULL AUTO_INCREMENT , 
                        `idgroup` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
                        `message` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
                        `period` INT NOT NULL , PRIMARY KEY (`id`)) 
                        ENGINE = InnoDB;
                """
        return sql
    

    @classmethod
    def get_sql_new_basket(cls, table_name: str) -> str:
        sql: str = f""" 
        CREATE TABLE IF NOT EXISTS e110kw29_kitopt.User_{table_name} 
        ( id INT NOT NULL AUTO_INCREMENT , 
        product_id TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, 
        photo TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, 
        user_id TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
        uniq_token TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
        user_name TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        name TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        datetime TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        category TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        data_type TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        brand TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        name_good TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        characteristic TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        count_on_stock INT NOT NULL , 
        count_on_order INT NOT NULL ,
        count_on_order_cats INT NOT NULL , 
        current_price DOUBLE NOT NULL, 
        price_from_1to2 DOUBLE NOT NULL , 
        price_from_3to4 DOUBLE NOT NULL , 
        price_from_5to9 DOUBLE NOT NULL , 
        price_from_10to29 DOUBLE NOT NULL , 
        price_from_30to69 DOUBLE NOT NULL , 
        price_from_70to149 DOUBLE NOT NULL , 
        price_from_150 DOUBLE NOT NULL , 
        sum_position DOUBLE NOT NULL , 
        delivery_method TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        price_delivery DOUBLE NOT NULL , 
        address_delivery TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        time_delivery TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
        pay_method TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        pay_status TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        order_status TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL , 
        receipt LONGBLOB NOT NULL,
        comment TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
        PRIMARY KEY (id)) ENGINE = InnoDB; """
        return sql
    
    @classmethod
    def get_sql_delete_table(cls, table_name: str) -> str:
        sql: str = f"DROP TABLE User_{table_name};"
        return sql
    
    @classmethod
    def get_sql_update_label(cls, usid: str, label: str, value: str):
        sql: str = f"UPDATE `e110kw29_kitopt`.`User_{usid}` SET {label} = '{value}'"
        return sql
    
    @classmethod
    def set_sql_spam_msg(cls, table_name: str) -> str:
        sql: str = f"""
                    INSERT INTO {table_name} (idgroup, message, period)
                    VALUES (%s, %s, %s);
                    """
        return sql
    

    @cdb
    async def set_message(self, cursor, *args, **kwargs) -> int:
        table = kwargs.get('table_name', 'Spam')
        msg = kwargs.get('msg', '')
        id_group = kwargs.get('id_group', '')
        period = kwargs.get('period', 0)
        try:
            sql = self.set_sql_spam_msg(table)
            cursor.execute(sql, [id_group, msg, period])
            
        except Error as e:
            print(f'\nError: db->set_message(). Exception = {e}\n')


    @cdb
    async def get_admin_auth(self, cursor, *args, **kwargs):
        id = kwargs.get('id', '')
        try:
            sql = f""" SELECT * FROM Admins WHERE tg_id='{id}'; """
            cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print(f'\nError: db->get_admin_auth(). Exception = {e}\n')
            return []
        

        

    @cdb
    async def delete_all_spam(self, cursor, *args, **kwargs):
        table = kwargs.get('table_name', 'Spam')
        try:
            sql = f""" TRUNCATE TABLE {table}; """
            cursor.execute(sql)
            
        except Error as e:
            print(f'\nError: db->delete_all_spam(). Exception = {e}\n')


    @cdb
    async def get_spam_table_data(self, cursor, *args, **kwargs):
        table_name = kwargs.get('table_name', 'Spam')
        try:
            cursor.execute(f""" SELECT * FROM {table_name}; """)
            return cursor.fetchall()
        except Error as e:
            print(f'\nError: db->get_spam_table_data(). Exception = {e}\n')
            return []
        

    @cdb
    async def get_basket(self, cursor, *args, **kwargs):
        table = kwargs.get('table_name')
        try:
            if not table:
                raise Exception('\nНе нашел table_name в db->get_basket()\n')
            sql: str = self.get_sql_basket(table)
            cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print(f'\nError: db->get_basket(). Exception = {e}\n')

    @cdb
    async def create_basket_table(self, cursor, *args, **kwargs):
        """Создать таблицу корзины заказа"""
        usid = kwargs.get('user_id')
        try:
            if not usid:
                raise Exception('\nНе нашел user_id в db->create_basket_table()\n')
            sqlreq: str = self.get_sql_new_basket(usid)
            return cursor.execute(sqlreq)
        except [Error, Exception] as e:
            print(f'\nError: db->create_basket_table(). Exception = {e}\n')
        
    @cdb
    async def delete_basket_table(self, cursor, *args, **kwargs):
        """Удалить таблицу корзины заказа"""
        usid = kwargs.get('user_id')
        try:
            if not usid:
                raise Exception('\nНе нашел user_id в db->delete_basket_table()\n')
            sql_delete: str = self.get_sql_delete_table(usid)
            return cursor.execute(sql_delete)
        except Error as e:
            print(f'\nError: db->delete_basket_table(). Exception = {e}\n')

    @cdb
    async def update_user_name(self, cursor, *args, **kwargs):
        """Обновить юзер нейм (@ тег) пользователя"""
        usid = kwargs.get('user_id')
        user_name = kwargs.get('user_name')
        try:
            if not usid or not user_name:
                raise Exception('\nНе нашел user_id и user_name в db->update_user_name()\n')
            sql_req = self.get_sql_update_label(usid, 'user_name', user_name)
            cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->update_user_name(). Exception = {e}\n')


    @cdb
    async def update_delivery_method(self, cursor, *args, **kwargs):
        """Изменить метод доставки"""
        usid = kwargs.get('user_id')
        delivery_method = kwargs.get('delivery_method')
        try:
            if not usid or not delivery_method:
                raise Exception('\nНе нашел user_id и delivery_method в db->change_delivery_method()\n')
            sql_req: str = self.get_sql_update_label(usid, 'delivery_method', delivery_method)
            return cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->change_delivery_method(). Exception = {e}\n')

    @cdb
    async def update_datetime_delivery(self, cursor, *args, **kwargs):
        """Изменить время и дату доставки"""
        usid = kwargs.get('user_id')
        delivery_datetime = kwargs.get('delivery_datetime')
        try:
            if not usid or not delivery_datetime:
                raise Exception('\nНе нашел user_id и delivery_datetime в db->update_datetime_delivery()\n')
            sql_req: str = self.get_sql_update_label(usid, 'time_delivery', delivery_datetime)
            return cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->change_datetime_delivery(). Exception = {e}\n')
    
    @cdb
    async def update_delivery_address(self, cursor, *args, **kwargs):
        """Изменить адрес доставки"""
        usid = kwargs.get('user_id')
        address_delivery = kwargs.get('delivery_address')
        try:
            if not usid or not address_delivery:
                raise Exception('\nНе нашел user_id и address_delivery в db->change_delivery_method()\n')
            sql_req: str = self.get_sql_update_label(usid, 'address_delivery', address_delivery)
            return cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->update_delivery_address(). Exception = {e}\n')
    
    @cdb
    async def update_comment(self, cursor, *args, **kwargs):
        """Изменить комментарий заказа"""
        usid = kwargs.get('user_id')
        comment = kwargs.get('comment')
        try:
            if not usid or not comment:
                raise Exception('\nНе нашел user_id и comment в db->update_comment()\n')
            sql_req: str = self.get_sql_update_label(usid, 'comment', comment)
            return cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->update_comment(). Exception = {e}\n')

    @cdb
    async def update_pay_method(self, cursor, *args, **kwargs):
        """Изменить способ оплаты заказа"""
        usid = kwargs.get('user_id')
        pay_method = kwargs.get('pay_method')
        try:
            if not usid or not pay_method:
                raise Exception('\nНе нашел user_id и pay_method в db->update_pay_method()\n')
            sql_req: str = self.get_sql_update_label(usid, 'pay_method', pay_method)
            return cursor.execute(sql_req)
        except Error as e:
            print(f'\nError: db->update_pay_method(). Exception = {e}\n')

    @cdb
    async def update_receipt(self, cursor, *args, **kwargs):
        """Изменить фото скриншота заказа"""
        usid = kwargs.get('user_id')
        photo = kwargs.get('photo')
        try:
            if not usid or not photo:
                raise Exception('\nНе нашел user_id и photo в db->update_receipt()\n')
            sql: str = f"UPDATE `e110kw29_kitopt`.`User_{usid}` SET receipt = %s"
            cursor.execute(sql, (photo,))
        except Error as e:
            print(f'\nError: db->update_receipt(). Exception = {e}\n')

    @cdb
    async def get_new_uniq_token(self, cursor, *args, **kwargs):
        """Получить новый номер заказа"""
        try:
            sql = f'SELECT * FROM `e110kw29_kitopt`.`Все_заказы`'
            cursor.execute(sql)
            all_orders = cursor.fetchall()
            max_uniq_token = 999
            for order in all_orders:
                max_uniq_token = max(max_uniq_token, int(order[4]))
            return max_uniq_token + 1 if max_uniq_token != 999 else 1000
        except Error as e:
            print(f'\nError: db->get_new_uniq_token(). Exception = {e}\n')

    @cdb
    async def transfer_basket_to_orders(self, cursor, *args, **kwargs):
        """Выгрузить"""
        usid = kwargs.get('user_id')
        data = kwargs.get('data')
        try:
            if not usid:
                raise Exception('\nНе нашел user_id в db->transfer_basket_to_orders()\n')
            for row in data:
                sql: str = f'''
                INSERT INTO `e110kw29_kitopt`.`Все_заказы`
                (product_id, photo, user_id, uniq_token, user_name, name, datetime, category, data_type, brand, name_good, characteristic, count_on_stock, count_on_order,
                count_on_order_cats, current_price, price_from_1to2, price_from_3to4, price_from_5to9, price_from_10to29, price_from_30to69, price_from_70to149, price_from_150,
                sum_position, delivery_method, price_delivery, address_delivery, time_delivery, pay_method, pay_status, order_status, receipt, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                row = list(row)
                row[4] = await self.get_new_uniq_token()
                cursor.execute(sql, row[1:])
        except Error as e:
            print(f'\nError: db->transfer_basket_to_orders(). Exception = {e}\n')

    @cdb
    async def update_pay_status(self, cursor, *args, **kwargs):
        """Изменить статус заказа"""
        usid = kwargs.get('user_id')
        status = kwargs.get('status')
        try:
            if not usid or not status:
                raise Exception('\nНе нашел user_id и status в db->update_pay_status()\n')
            sqlreq = self.get_sql_update_label(usid, 'pay_status', status)
            cursor.execute(sqlreq)
        except Error as e:
            print(f'\nError: db->update_pay_status(). Exception = {e}\n')

    @cdb
    async def update_pay_method(self, cursor, *args, **kwargs):
        """Изменить метод оплаты заказа"""
        usid = kwargs.get('user_id')
        pay_method = kwargs.get('pay_method')
        try:
            if not usid or not pay_method:
                raise Exception('\nНе нашел user_id и pay_method в db->update_pay_method()\n')
            sqlreq = self.get_sql_update_label(usid, 'pay_method', pay_method)
            cursor.execute(sqlreq)
        except Error as e:
            print(f'\nError: db->update_pay_method(). Exception = {e}\n')

    @cdb
    async def update_order_status(self, cursor, *args, **kwargs):
        """Изменить статус заказа"""
        usid = kwargs.get('user_id')
        status = kwargs.get('status')
        try:
            if not usid or not status:
                raise Exception('\nНе нашел user_id и status в db->update_order_status()\n')
            sqlreq = self.get_sql_update_label(usid, 'order_status', status)
            cursor.execute(sqlreq)
        except Error as e:
            print(f'\nError: db->update_order_status(). Exception = {e}\n')
