from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json
from datetime import datetime
import pytz
taiwan_tz = pytz.timezone('Asia/Taipei')
taiwan_time = datetime.now(taiwan_tz)
weekday = 0 if taiwan_time.weekday() == 6 else taiwan_time.weekday() + 1
class Restaurant(BaseModel):
    id : int
    place_id : Optional[str] = None
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
    distance : Optional[int] = None
    attitude : Optional[str] = None

class RestaurantOut(BaseModel):
    data : List[Restaurant]
    next_page : Optional[int] = None
class CardModel:
    def get_suggest_restaurants_info(
            min_google_rating,
            min_rating_count,
            user_lat, 
            user_lng,
            restaurant_type,
            distance_limit,
            user_id,
            day_of_week = weekday
        ):

        # 預設在小樹屋中
        if user_lat is None:
            user_lat = 25.062673934754084
        if user_lng is None:
            user_lng = 121.52174308176814


        sql = """
            SELECT DISTINCT
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
                i.urls,
                p.attitude,
                ST_Distance_Sphere(r.coordinates, POINT(%s, %s)) AS distance
            FROM 
                restaurants AS r
            LEFT JOIN 
                (SELECT 
                    place_id, 
                    JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'open_time', TIME_FORMAT(open_time, '%H:%\i:%\s'), 
                            'close_time', TIME_FORMAT(close_time, '%H:%\i:%\s')
                        ) 
                    ) AS opening_hours 
                FROM 
                    opening_hours 
                WHERE 
                    day_of_week = %s
                GROUP BY 
                    place_id) AS o 
            ON r.place_id = o.place_id 
            LEFT JOIN 
                (SELECT
                    place_id, 
                    JSON_ARRAYAGG(url) AS urls 
                FROM 
                    images
                WHERE
                    upload_by_user = 0
                GROUP BY 
                    place_id) AS i 
            ON r.place_id = i.place_id
            LEFT JOIN pockets AS p 
            ON r.id = p.restaurant_id AND p.user_id = %s
            WHERE
                r.businessStatus = 1 
                AND (p.attitude IS NULL OR p.attitude != 'dislike')
        """

        # 參數列表
        params = [user_lng, user_lat, day_of_week, user_id] 

        # 餐廳類型，評分，評分數判斷
        if min_google_rating is not None:
            sql += " AND r.google_rating >= %s"
            params.append(min_google_rating)

        if min_rating_count is not None:
            sql += " AND r.google_rating_count >= %s"
            params.append(min_rating_count)

        if restaurant_type != "*" and restaurant_type is not None:
            sql += " AND r.type = %s"
            params.append(restaurant_type)

        # 距離條件判斷
        if distance_limit is not None:
            sql += " HAVING distance <= %s"
            params.append(distance_limit)

        # 排序和限制
        sql += " ORDER BY RAND() LIMIT 10;"

        # 將val參數轉成tuple並查詢資料庫
        result = Database.read_all(sql, tuple(params))
        
        # 資料格式處裡
        restaurant_group = []
        print(f'推薦回傳比數: {len(result)}')

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
                currentTime = taiwan_time.strftime("%H:%M:%S")
                for opening_hour in result[i]["opening_hours"]:
                    if opening_hour["open_time"] < currentTime and currentTime < opening_hour["close_time"]:
                        open = True
                        break
            
            # 處裡距離格式
            distance = int(round(result[i]["distance"], -1))


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
                    reservable=result[i]["reservable"],
                    distance=distance,
                    attitude = result[i]["attitude"]
                )
            )

        return RestaurantOut(data=restaurant_group)

    def get_restaurant_by_id(id, day_of_week = weekday):
        sql = """
        SELECT 
            r.id,
            r.place_id, 
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
            (SELECT * FROM restaurants WHERE id = %s) AS r
        LEFT JOIN 
            (SELECT 
                place_id, 
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'day_of_week', day_of_week, 
                        'open_time', TIME_FORMAT(open_time, '%H:%\i:%\s'), 
                        'close_time', TIME_FORMAT(close_time, '%H:%\i:%\s')
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
            WHERE
                upload_by_user = 0
            GROUP BY 
                place_id) AS i 
        ON r.place_id = i.place_id;
        """
        val = (id,)
        result = Database.read_one(sql, val)



        # 處裡圖片格式
        if result["urls"] is not None:
            result["urls"] = json.loads(result["urls"])
            img_urls = result["urls"][::-1]     
        else:
            img_urls = None

        # 確認營業狀況
        open = None;
        if result["opening_hours"] is not None:
            open = False
            result["opening_hours"] = json.loads(result["opening_hours"])
            for opening_hour in result["opening_hours"]:
                if opening_hour["day_of_week"] == day_of_week:
                    currentTime = taiwan_time.strftime("%H:%M:%S")
                    if opening_hour["open_time"] < currentTime and currentTime < opening_hour["close_time"]:
                        open = True
                        break


        restaurant = Restaurant(
            id=result["id"],
            place_id=result["place_id"],
            imgs=img_urls, 
            name=result["name"], 
            open=open, 
            restaurant_type=result["type"], 
            google_rating=result["google_rating"], 
            google_rating_count=result["google_rating_count"],
            address=result["address"],
            takeout=result["takeout"],
            dineIn=result["dineIn"],
            delivery=result["delivery"],
            reservable=result["reservable"]
        )  

        return restaurant

    def get_search_restaurants_info(
            keyword:str, 
            page:int,
            user_lat, 
            user_lng,
            user_id,
            day_of_week = weekday
            ):
        keyword = '%' + keyword + '%'
        offset = page * 10

        # 預設在小樹屋中
        if user_lat is None:
            user_lat = 25.062673934754084
        if user_lng is None:
            user_lng = 121.52174308176814

        sql = """
        SELECT 
            r.id,
            r.place_id, 
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
            i.urls,
            p.attitude,
            ST_Distance_Sphere(r.coordinates, POINT(%s, %s)) AS distance
        FROM 
            (SELECT * FROM restaurants WHERE name LIKE %s LIMIT %s, 11) AS r
        LEFT JOIN 
            (SELECT 
                place_id, 
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'open_time', TIME_FORMAT(open_time, '%H:%\i:%\s'), 
                        'close_time', TIME_FORMAT(close_time, '%H:%\i:%\s')
                    ) 
                ) AS opening_hours 
            FROM 
                opening_hours 
            WHERE 
                day_of_week = %s
            GROUP BY 
                place_id) AS o 
        ON r.place_id = o.place_id 
        LEFT JOIN 
            (SELECT
                place_id, 
                JSON_ARRAYAGG(url) AS urls 
            FROM 
                images
            WHERE
                upload_by_user = 0
            GROUP BY 
                place_id) AS i 
        ON r.place_id = i.place_id
        LEFT JOIN pockets AS p 
        ON r.id = p.restaurant_id AND p.user_id = %s;
        """
        val = (user_lng, user_lat,keyword, offset, day_of_week, user_id)
        result = Database.read_all(sql, val)
        print(f'搜尋{keyword}回傳比數: {len(result)}')
        # 判斷 next_page
        if len(result) < 11:
            next_page = None
        else:
            next_page = page+1
        length = len(result) -1 if next_page is not None else len(result)
        
        restaurant_group = []


        for i in range(length):

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
                currentTime = taiwan_time.strftime("%H:%M:%S")
                for opening_hour in result[i]["opening_hours"]:
                    if opening_hour["open_time"] < currentTime and currentTime < opening_hour["close_time"]:
                        open = True
                        break
            
            # 處裡距離格式
            distance = int(round(result[i]["distance"], -1))

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
                    reservable=result[i]["reservable"],
                    distance=distance,
                    attitude = result[i]["attitude"]
                )
            )

        return RestaurantOut(data=restaurant_group, next_page=next_page)
