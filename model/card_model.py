from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json
from datetime import datetime
import random

class Restaurant(BaseModel):
    id : int
    name : str
    open : Optional[bool]
    restaurant_type : str
    google_rating : Optional[float]
    google_rating_count : Optional[int]
    imgs : Optional[List]
    address : str
    takeout : Optional[bool]
    dineIn : Optional[bool]
    delivery : Optional[bool]
    reservable : Optional[bool]



class RestaurantOut(BaseModel):
    data : List[Restaurant]

class CardModel:
    def get_restaurants_info(day_of_week = datetime.today().weekday() + 1):
        
        # 隨機選擇餐廳id
        random_id = []
        for i in range(10):
            random_id.append(str(random.randint(1,4117)))
        
        suggest_id = ", ".join(random_id)
        sql = (f"""
        SELECT 
            r.id, 
            r.name, 
            r.type,
            r.google_rating, 
            r.google_rating_count,
            r.address,
            r.takeout,
            r.dineIn,
            r.delivery,
            r.reservable,
            o.opening_hours, 
            i.urls 
        FROM 
            (SELECT * FROM restaurants WHERE id in ({suggest_id}) and businessStatus = 1) AS r
        LEFT JOIN 
            (SELECT 
                place_id, 
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'day_of_week', day_of_week, 
                        'open_time', TIME_FORMAT(open_time, '%H:%i:%s'), 
                        'close_time', TIME_FORMAT(close_time, '%H:%i:%s')
                    ) 
                ) AS opening_hours 
            FROM 
                opening_hours 
            GROUP BY 
                place_id) AS o 
            ON r.place_id = o.place_id 
        LEFT JOIN 
            (SELECT
                place_id, 
                JSON_ARRAYAGG(url) AS urls 
            FROM 
                images
            GROUP BY 
                place_id) AS i 
            ON r.place_id = i.place_id;
        """)
        result = Database.read_all(sql)
        
        # 資料格式處裡
        restaurant_group = []
        print(f'回傳比數: {len(result)}')

        for i in range(len(result)):

            # 處裡圖片格式
            if result[i]["urls"] is not None:
                result[i]["urls"] = json.loads(result[i]["urls"])
                img_urls = result[i]["urls"][::-1]     
            else:
                img_urls = None

            # 確認營業狀況
            open = None;
            if result[i]["opening_hours"] is not None:
                open = False
                result[i]["opening_hours"] = json.loads(result[i]["opening_hours"])
                for opening_hour in result[i]["opening_hours"]:
                    if opening_hour["day_of_week"] == day_of_week:
                        currentTime = datetime.now().strftime("%H:%M:%S")
                        if opening_hour["open_time"] < currentTime and currentTime < opening_hour["close_time"]:
                            open = True
                            break
            
            restaurant_group.append(
                Restaurant(
                    id=result[i]["id"], 
                    imgs=img_urls, 
                    name=result[i]["name"], 
                    open=open, 
                    restaurant_type=result[i]["type"], 
                    google_rating=result[i]["google_rating"], 
                    google_rating_count=result[i]["google_rating_count"],
                    address=result[i]["address"],
                    takeout=result[i]["takeout"],
                    dineIn=result[i]["dineIn"],
                    delivery=result[i]["delivery"],
                    reservable=result[i]["reservable"]
                )
            )

        return RestaurantOut(data=restaurant_group)

