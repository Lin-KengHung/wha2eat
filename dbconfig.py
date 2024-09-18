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
