import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()

# DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_HOST = "localhost"
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')


class Database:
    mydb = {
        "host" : DATABASE_HOST,
        "user" : DATABASE_USER,
        "password" : DATABASE_PASSWORD,
        "database" : DATABASE_NAME
    }
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=32, **mydb)
    
    def read_all(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        mycursor.close()
        connect.close()
        return result
    
    def read_one(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        mycursor.close()
        connect.close()
        return result

    def create(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        connect.commit()
        affected_rows = mycursor.rowcount
        mycursor.close()
        connect.close()
        return affected_rows
    
    def create_and_return_id(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        last_id = mycursor.lastrowid
        connect.commit()
        mycursor.close()
        connect.close()
        return last_id
    
    def update(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        connect.commit()
        affected_rows = mycursor.rowcount
        mycursor.close()
        connect.close()
        return affected_rows
    
    def delete(sql, val=None):
        connect = Database.connection_pool.get_connection()
        mycursor = connect.cursor(dictionary=True)
        mycursor.execute(sql, val)
        connect.commit()
        affected_rows = mycursor.rowcount
        mycursor.close()
        connect.close()
        return affected_rows
