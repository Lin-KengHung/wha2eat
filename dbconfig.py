import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()



class Database:
    mydb = {
        "host" : "localhost",
        "user" : "root",
        "password" : os.getenv("PASSWORD"),
        "database" : "wha2eat_ncku"
    }
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=15, **mydb)
    
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
