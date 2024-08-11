from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json


class Match(BaseModel):
    user_id: int
    restaurant_id: int
    attitude : str

class PocketModel:
    def record_match(user_id, restaurant_id, attitude):
        sql = """
        INSERT INTO pockets (user_id, restaurant_id, attitude) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY 
        UPDATE 
        attitude = %s, 
        update_at = CURRENT_TIMESTAMP;
        """
        val = (user_id, restaurant_id, attitude, attitude)
        result = Database.create(sql, val)
        if (result > 0):
            return True
        else:
            return False


