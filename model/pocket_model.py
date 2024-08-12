from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json
from datetime import datetime


class Match(BaseModel):
    user_id: int
    restaurant_id: int
    attitude : str

class FavorRestaurants(BaseModel):
    id: int
    name: str
    img: str
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

    def get_my_pocket(id, page, day_of_week=datetime.today().weekday() + 1):

        offset = page * 10
        sql = f"""
        SELECT 
            p.restaurant_id, 
            r.name, 
            i.url, 
            o.opening_hours
        FROM 
            (SELECT * FROM pockets WHERE user_id = {id} AND attitude = "like" ORDER BY update_at DESC LIMIT {offset}, 11) AS p 
        
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
        LEFT JOIN 
            (SELECT 
                place_id, 
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'open_time', TIME_FORMAT(open_time, '%H:%i:%s'), 
                        'close_time', TIME_FORMAT(close_time, '%H:%i:%s')
                    )
                ) AS opening_hours 
            FROM 
                opening_hours 
            WHERE 
                day_of_week = {day_of_week}
            GROUP BY 
                place_id) AS o ON r.place_id = o.place_id
        ORDER BY p.update_at DESC;
        """

        result = Database.read_all(sql)

        # 判斷 next_page
        if len(result) < 11:
            next_page = None
        else:
            next_page = page+1


        restaurant_group = []
        for i in range(len(result)-1):
            # 確認營業狀況
            open = None;
            if result[i]["opening_hours"] is not None:
                open = False
                result[i]["opening_hours"] = json.loads(result[i]["opening_hours"])
                currentTime = datetime.now().strftime("%H:%M:%S")
                for opening_hour in result[i]["opening_hours"]:
                    if opening_hour["open_time"] < currentTime and currentTime < opening_hour["close_time"]:
                        open = True
                        break
            
            restaurant_group.append(
                FavorRestaurants(
                    id=result[i]["restaurant_id"], 
                    name=result[i]["name"],
                    img=result[i]["url"],
                    open=open, 
                )
            )
        return RestaurantsGroup(data=restaurant_group, next_page=next_page)