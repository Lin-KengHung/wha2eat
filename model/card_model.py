from dbconfig import Database
from pydantic import BaseModel, Field
from typing import Optional, List
import json
from datetime import datetime
import pytz
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
pd.set_option('future.no_silent_downcasting', True)

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
        print(taiwan_time)

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
        

class CollaborativeFiltering:
    def user_base_suggest(user_id):
        sql = """
            -- 定義一個公共表達式 (CTE)，方便其他子查詢使用，此查詢結果為使用者已標記為 'like' 的所有餐廳ID
            WITH liked_restaurants AS (
                SELECT restaurant_id 
                FROM pockets 
                WHERE user_id = %s AND attitude = 'like' 
            )

            -- 主查詢，根據合併的配對總分，去掉已經喜歡的餐廳後推薦餐廳
            SELECT 
                recommended_restaurant_id, 
                SUM(pair_count) AS pair_count  -- 對配對次數進行求和，以統計配對的總數
            FROM (
                -- 子查詢：計算兩兩餐廳配對次數，根據特定使用者口袋名單的每一餐廳，計算其他餐廳的配對總分
                SELECT 
                    CASE 
                        -- 如果餐廳id1在使用者的喜好清單中，推薦餐廳id2
                        WHEN restaurant_id_1 IN (SELECT restaurant_id FROM liked_restaurants) THEN restaurant_id_2
                        -- 如果餐廳id2在使用者的喜好清單中，推薦餐廳id1
                        WHEN restaurant_id_2 IN (SELECT restaurant_id FROM liked_restaurants) THEN restaurant_id_1
                    END AS recommended_restaurant_id,
                    pair_count  -- 各餐廳配對次數
                FROM (
                    -- 查詢兩兩餐廳在單一使用者中的配對次數，保留配對結果，並總和所有使用者的配對次數
                    SELECT 
                        p1.restaurant_id AS restaurant_id_1, 
                        p2.restaurant_id AS restaurant_id_2, 
                        COUNT(*) AS pair_count  
                    FROM 
                        pockets p1
                    JOIN 
                        pockets p2 ON p1.user_id = p2.user_id AND p1.restaurant_id < p2.restaurant_id  -- 避免餐廳id重複配對
                    WHERE 
                        p1.attitude = 'like' AND p2.attitude = 'like'  -- 僅考慮喜歡的餐廳 
                    GROUP BY 
                        p1.restaurant_id, p2.restaurant_id  
                    HAVING 
                        COUNT(*) >= %s 
                ) AS pair_table
                WHERE 
                    CASE 
                        -- 僅保留有效的推薦結果
                        WHEN restaurant_id_1 IN (SELECT restaurant_id FROM liked_restaurants) THEN restaurant_id_2
                        WHEN restaurant_id_2 IN (SELECT restaurant_id FROM liked_restaurants) THEN restaurant_id_1
                    END IS NOT NULL  -- 排除沒有推薦結果的情況
            ) AS recommended_pairs
            WHERE 
                recommended_restaurant_id NOT IN (SELECT restaurant_id FROM liked_restaurants)  -- 排除已經喜歡的
            GROUP BY 
                recommended_restaurant_id 
            ORDER BY 
                pair_count DESC; 
        """
        val = (user_id,1)
        results = Database.read_all(sql,val)
        recommendations= []

        for result in results:
            recommendations.append(result["recommended_restaurant_id"])
            # print(result["recommended_restaurant_id"])
        return recommendations

    def item_base_suggest(user_id):
        # 計算使用者評分紀錄
        sql_4_user_rating = """
            SELECT
                p.user_id,
                p.restaurant_id,
                CASE
                    WHEN p.attitude = 'like' THEN 5
                    WHEN p.attitude = 'consider' THEN 2.5
                    WHEN p.attitude = 'dislike' THEN 0
                    ELSE 0
                END +
                CASE
                    WHEN c.rating = 5 THEN 5
                    WHEN c.rating = 4 THEN 3
                    WHEN c.rating = 3 THEN 1
                    WHEN c.rating = 2 THEN -2
                    WHEN c.rating = 1 THEN -4
                    ELSE 0
                END AS total_score
            FROM
                pockets p
            LEFT JOIN
                comments c
            ON
                p.user_id = c.user_id AND p.restaurant_id = c.restaurant_id;
            """
            
        ratings_result = Database.read_all(sql_4_user_rating)
        restaurant_ids = [row['restaurant_id'] for row in ratings_result]

        # 獲得餐廳的google評分
        sql_4_google_rating = """
            SELECT
                id AS restaurant_id,
                google_rating
            FROM
                restaurants
            WHERE
                id IN (%s);
            """ % ','.join([str(id) for id in restaurant_ids])

        google_rating_result = Database.read_all(sql_4_google_rating)

        # 建立google 評分字典，NaN用2.5取代(與consider分數相同)
        google_rating_dict = {
            row['restaurant_id']: float(row['google_rating']) if row['google_rating'] is not None else 2.5
            for row in google_rating_result
        }

        # 構建使用者對餐廳評分 DataFrame
        df = pd.DataFrame(ratings_result)
        pivot_table = df.pivot_table(index='restaurant_id', columns='user_id', values='total_score')

        # 紀錄特定使用者尚未評價或曾考慮過的餐廳
        unrated_or_considered_restaurants = pivot_table[user_id][(pivot_table[user_id].isna()) | (pivot_table[user_id] == 2.5)].index.tolist()

        # 紀錄特定使用者喜歡的(分數 >=5)的餐廳
        high_score_restaurants = pivot_table[user_id][pivot_table[user_id] >= 5].index.tolist()

        # 使用 Google Rating 填充 NaN 值
        pivot_table_filled = pivot_table.apply(lambda row: row.fillna(google_rating_dict.get(row.name)), axis=1)

        # 計算餐廳之間的餘弦相似度
        cosine_sim_matrix = cosine_similarity(pivot_table_filled)

        # 將相似度矩陣轉換成 restaurant_id x restaurant_id 的 DataFrame
        cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=pivot_table.index, columns=pivot_table.index)
        
        def recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants, top_n=3):
            recommended_restaurants = set()
            
            for restaurant_id in high_score_restaurants:
                
                # 找到與此餐廳相似的餐廳
                similar_restaurants = cosine_sim_df[restaurant_id].sort_values(ascending=False).index.tolist()
                
                # 過濾出尚未評價的餐廳
                similar_unrated_or_considered_restaurants = [r for r in similar_restaurants if r in unrated_or_considered_restaurants]
                
                # 添加到推薦列表
                recommended_restaurants.update(similar_unrated_or_considered_restaurants[:top_n])
            
            return list(recommended_restaurants)
    
        recommendations = recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants)
        return recommendations
