from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json

class Match(BaseModel):
    user_id: int
    restaurant_id: int
    attitude : str

class FavorRestaurants(BaseModel):
    id: int
    name: str
    img: Optional[str] = None
    open : Optional[bool]


class RestaurantsGroup(BaseModel):
    data: List[FavorRestaurants]
    next_page: Optional[int] = None
    


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

    def get_my_pocket(id, page):

        offset = page * 10
        sql = """
        SELECT 
            p.restaurant_id, 
            r.name, 
            i.url, 
            CASE 
                WHEN NOT EXISTS (
                    SELECT 1 
                    FROM opening_hours AS o
                    WHERE 
                        o.place_id = r.place_id 
                ) THEN NULL
                WHEN EXISTS (
                    SELECT 1 
                    FROM opening_hours AS o
                    WHERE 
                        o.place_id = r.place_id 
                        AND o.day_of_week = MOD(DAYOFWEEK(NOW()), 7)
                        AND o.open_time <= CURTIME()
                        AND o.close_time > CURTIME()
                ) THEN TRUE
                ELSE FALSE
            END AS is_open
        FROM 
            (SELECT * FROM pockets WHERE user_id = %s AND attitude = "like" ORDER BY update_at DESC LIMIT %s, 11) AS p 
        
        LEFT JOIN 
            restaurants AS r ON p.restaurant_id = r.id 
        LEFT JOIN 
            (SELECT 
                i1.place_id, 
                i1.url 
            FROM 
                images AS i1
            WHERE 
                i1.id = (
                    SELECT 
                        MIN(i2.id) 
                    FROM 
                        images AS i2 
                    WHERE 
                        i2.place_id = i1.place_id
                )
            ) AS i ON r.place_id = i.place_id
        ORDER BY p.update_at DESC;
        """
        val = (id, offset)
        result = Database.read_all(sql, val)
        # 判斷 next_page
        if len(result) < 11:
            next_page = None
        else:
            next_page = page+1

        length = len(result) -1 if next_page is not None else len(result)
        restaurant_group = []
        for i in range(length):
            
            restaurant_group.append(
                FavorRestaurants(
                    id=result[i]["restaurant_id"], 
                    name=result[i]["name"],
                    img=result[i]["url"],
                    open=result[i]["is_open"], 
                )
            )
        
        return RestaurantsGroup(data=restaurant_group, next_page=next_page)
    
    def delete_favor_restaurant(restaurant_id, user_id):
        sql = 'DELETE FROM pockets WHERE user_id = %s and restaurant_id = %s and attitude = "like";'
        val = (user_id, restaurant_id)
        result = Database.delete(sql, val)
        if result > 0:
            return True
        else:
            return False
