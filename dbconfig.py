import mysql.connector
import os
import redis
import json
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler



load_dotenv()

DATABASE_HOST = os.getenv('DATABASE_HOST')
# DATABASE_HOST = "localhost"
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
REDIS_HOST = os.getenv('REDISHOST')

class Database:
    mydb = {
        "host": DATABASE_HOST,
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
        "database": DATABASE_NAME
    }
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=32, **mydb)

    @staticmethod
    def read_all(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute("SET time_zone = 'Asia/Taipei';")
            mycursor.execute(sql, val)
            result = mycursor.fetchall()
            return result
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()

    @staticmethod
    def read_one(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute("SET time_zone = 'Asia/Taipei';")
            mycursor.execute(sql, val)
            result = mycursor.fetchone()
            return result
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()

    @staticmethod
    def create(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute(sql, val)
            connect.commit()
            affected_rows = mycursor.rowcount
            return affected_rows
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()

    @staticmethod
    def create_and_return_id(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute(sql, val)
            last_id = mycursor.lastrowid
            connect.commit()
            return last_id
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()

    @staticmethod
    def update(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute(sql, val)
            connect.commit()
            affected_rows = mycursor.rowcount
            return affected_rows
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()

    @staticmethod
    def delete(sql, val=None):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.execute(sql, val)
            connect.commit()
            affected_rows = mycursor.rowcount
            return affected_rows
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()
    
    @staticmethod
    def update_many(sql, val):
        connect = None
        mycursor = None
        try:
            connect = Database.connection_pool.get_connection()
            mycursor = connect.cursor(dictionary=True)
            mycursor.executemany(sql, val)
            connect.commit()
            affected_rows = mycursor.rowcount
            return affected_rows
        finally:
            if mycursor:
                mycursor.close()
            if connect:
                connect.close()


redis_client = redis.Redis(host= REDIS_HOST, port=6379, db=0)
class RedisCache:
    
    @classmethod
    def record_pockets(cls, user_id, restaurant_id, attitude):
    # 構造暫存資料
        key = f"user:{user_id}:pockets"
        field = f"{restaurant_id}"  
        redis_client.hset(key, field, attitude)  
        return True
    
    @classmethod
    def batch_write_pockets_to_db(cls, user_id):
        key = f"user:{user_id}:pockets"
        fields = redis_client.hkeys(key)
        records = []

        for field in fields:
            attitude = redis_client.hget(key, field).decode('utf-8') 
            records.append((user_id, field, attitude)) # field == restaurant_id

        if records:
            sql = """
                INSERT INTO pockets (user_id, restaurant_id, attitude) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                attitude = VALUES(attitude), 
                update_at = CURRENT_TIMESTAMP;
            """
            row = Database.update_many(sql, records)
            print(f"更新了{row}行")
            redis_client.delete(key)

        return True
    
    @classmethod
    def batch_write_all_users_to_db(cls):
        print("定時更新")
        keys = redis_client.keys("user:*:pockets")
        for key in keys:
            key = key.decode('utf-8')
            user_id = key.split(":")[1]
            cls.batch_write_pockets_to_db(user_id)

    @classmethod
    def start_scheduler(cls):
        # 初始化並啟動定時器
        scheduler = BackgroundScheduler()
        # 設置每隔10分鐘調用一次批量同步
        scheduler.add_job(cls.batch_write_all_users_to_db, 'interval', days=1)
        # 啟動調度器
        scheduler.start()

RedisCache.batch_write_all_users_to_db()