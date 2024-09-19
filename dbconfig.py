import mysql.connector
import os
import redis
import json
from dotenv import load_dotenv


load_dotenv()

DATABASE_HOST = os.getenv('DATABASE_HOST')
# DATABASE_HOST = "localhost"
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')


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


redis_client = redis.Redis(host= DATABASE_HOST, port=6379, db=0)
class RedisCache:
    def record_pockets(user_id, restaurant_id, attitude):
    # 構造暫存資料
        key = f"record:{user_id}:{restaurant_id}"
        value = json.dumps({
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "attitude": attitude
        })
        
        # 暫存資料到 Redis
        redis_client.set(key, value)
        return True

    def batch_write_pockets_to_db():
        keys = redis_client.keys("record:*")
        records = []

        for key in keys:
            record = redis_client.get(key)
            record_data = json.loads(record)
            records.append((record_data["user_id"], record_data["restaurant_id"], record_data["attitude"]))

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
            redis_client.delete(*keys)

        return True