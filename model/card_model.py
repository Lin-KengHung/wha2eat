from dbconfig import Database,RedisCache
from model.utils import recommend_restaurants_for_user, calculate_cosine_similarity
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
pd.set_option('future.no_silent_downcasting', True)


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
    data : List
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
            have_seen,
            is_open,
            restaurant_id_list
        ):
        
        # 更新快取中使用者口袋清單
        RedisCache.batch_write_pockets_to_db()

        # 預設在小樹屋中
        if user_lat is None:
            user_lat = 25.062673934754084
        if user_lng is None:
            user_lng = 121.52174308176814

        sql = """
            SELECT DISTINCT
                r.id,
                r.place_id, 
                r.name, 
                r.google_rating, 
                r.google_rating_count,
                r.address,
                r.takeout,
                r.dineIn,
                r.delivery,
                r.reservable,
                i.urls,
                p.attitude,
                ST_Distance_Sphere(r.coordinates, POINT(%s, %s)) AS distance,
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
                END AS is_open,
                CASE 
                    WHEN r.type IN ('法式餐廳', '西班牙餐廳', '墨西哥餐廳','中東餐廳', '土耳其餐廳', '巴西餐廳','地中海餐廳', '印度餐廳') THEN '異國餐廳'
                    WHEN r.type IN ('日式餐廳', '壽司', '拉麵') THEN '日式餐廳'
                    WHEN r.type IN ('中式餐廳', '海鮮餐廳') THEN '中式餐廳'
                    WHEN r.type IN ('美式餐廳', '披薩', '三明治店', '漢堡餐廳') THEN '美式餐廳'
                    WHEN r.type IN ('泰式餐廳', '印尼餐廳', '越南餐廳') THEN '東南亞餐廳'
                    ELSE r.type
                END AS restaurant_type
            FROM 
                restaurants AS r
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
        """

        # 參數列表
        params = [user_lng, user_lat, user_id] 

        # 判斷有沒有看過，以及需不需要有or沒看過或不限制
        if have_seen is True:
            sql += " AND p.attitude != 'dislike'"
        elif have_seen is False:
            sql += " AND p.attitude IS NULL"
        else:
            sql += " AND (p.attitude IS NULL OR p.attitude != 'dislike')"


        # google評分篩選
        if min_google_rating is not None:
            sql += " AND r.google_rating >= %s"
            params.append(min_google_rating)

        # google評分數量篩選
        if min_rating_count is not None:
            sql += " AND r.google_rating_count >= %s"
            params.append(min_rating_count)

        # 限制只能在推薦的餐廳list中
        if restaurant_id_list:
            sql += " AND r.id IN (%s)" % ','.join(['%s'] * len(restaurant_id_list))
            params.extend(restaurant_id_list)

        # 距離條件，是否營業，餐廳類型篩選
        if distance_limit is not None or is_open is True or (restaurant_type != "*" and restaurant_type is not None):
            sql += " HAVING "
            conditions = []
            if distance_limit is not None:
                conditions.append("distance <= %s")
                params.append(distance_limit)
            if is_open is True:
                conditions.append("is_open = TRUE")
            if restaurant_type != "*" and restaurant_type is not None:
                conditions.append("restaurant_type = %s")
                params.append(restaurant_type)
            sql += " AND ".join(conditions)


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
            
            # 處裡距離格式
            distance = int(round(result[i]["distance"], -1))

            restaurant_group.append(
                Restaurant(
                    id=result[i]["id"],
                    place_id=result[i]["place_id"],
                    imgs=img_urls, 
                    name=result[i]["name"], 
                    open=result[i]["is_open"], 
                    restaurant_type=result[i]["restaurant_type"], 
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

    def get_restaurant_by_id(restaurant_id, user_id, user_lat=None, user_lng=None):
        
        # 更新快取中使用者口袋清單
        RedisCache.batch_write_pockets_to_db()

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
            i.urls,
            p.attitude,
            ST_Distance_Sphere(r.coordinates, POINT(%s, %s)) AS distance,
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
            END AS is_open,
            CASE 
                WHEN r.type IN ('法式餐廳', '西班牙餐廳', '墨西哥餐廳','中東餐廳', '土耳其餐廳', '巴西餐廳','地中海餐廳', '印度餐廳') THEN '異國餐廳'
                WHEN r.type IN ('日式餐廳', '壽司', '拉麵') THEN '日式餐廳'
                WHEN r.type IN ('中式餐廳', '海鮮餐廳') THEN '中式餐廳'
                WHEN r.type IN ('美式餐廳', '披薩', '三明治店', '漢堡餐廳') THEN '美式餐廳'
                WHEN r.type IN ('泰式餐廳', '印尼餐廳', '越南餐廳') THEN '東南亞餐廳'
                ELSE r.type
            END AS restaurant_type
        FROM 
            (SELECT * FROM restaurants WHERE id = %s) AS r
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
        val = [user_lng, user_lat, restaurant_id, user_id]

        result = Database.read_one(sql, tuple(val))
        print(result["distance"])


        # 處裡圖片格式
        if result["urls"] is not None:
            result["urls"] = json.loads(result["urls"])
            img_urls = result["urls"][::-1]     
        else:
            img_urls = None
        # 處裡距離格式
        distance = int(round(result["distance"], -1))

        restaurant = Restaurant(
            id=result["id"],
            place_id=result["place_id"],
            imgs=img_urls, 
            name=result["name"], 
            open=result["is_open"], 
            restaurant_type=result["type"], 
            google_rating=result["google_rating"], 
            google_rating_count=result["google_rating_count"],
            address=result["address"],
            takeout=result["takeout"],
            dineIn=result["dineIn"],
            delivery=result["delivery"],
            reservable=result["reservable"],
            distance=distance,
            attitude=result["attitude"]
        )  

        return restaurant

    def get_search_restaurants_info(
            keyword:str, 
            page:int,
            user_lat, 
            user_lng,
            user_id,
            ):
        
        # 更新快取中使用者口袋清單
        RedisCache.batch_write_pockets_to_db()

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
            r.google_rating, 
            r.google_rating_count,
            r.address,
            r.takeout,
            r.dineIn,
            r.delivery,
            r.reservable,
            i.urls,
            p.attitude,
            ST_Distance_Sphere(r.coordinates, POINT(%s, %s)) AS distance,
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
            END AS is_open,
            CASE 
                WHEN r.type IN ('法式餐廳', '西班牙餐廳', '墨西哥餐廳','中東餐廳', '土耳其餐廳', '巴西餐廳','地中海餐廳', '印度餐廳') THEN '異國餐廳'
                WHEN r.type IN ('日式餐廳', '壽司', '拉麵') THEN '日式餐廳'
                WHEN r.type IN ('中式餐廳', '海鮮餐廳') THEN '中式餐廳'
                WHEN r.type IN ('美式餐廳', '披薩', '三明治店', '漢堡餐廳') THEN '美式餐廳'
                WHEN r.type IN ('泰式餐廳', '印尼餐廳', '越南餐廳') THEN '東南亞餐廳'
                ELSE r.type
            END AS restaurant_type
        FROM 
            (SELECT * FROM restaurants WHERE name LIKE %s LIMIT %s, 11) AS r
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
        val = (user_lng, user_lat,keyword, offset, user_id)
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
            
            # 處裡距離格式
            distance = int(round(result[i]["distance"], -1))

            restaurant_group.append(
                Restaurant(
                    id=result[i]["id"],
                    place_id=result[i]["place_id"],  
                    imgs=img_urls, 
                    name=result[i]["name"], 
                    open=result[i]["is_open"], 
                    restaurant_type=result[i]["restaurant_type"], 
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
        print(results)
        recommendations= []

        for result in results:
            recommendations.append(result["recommended_restaurant_id"])
            # print(result["recommended_restaurant_id"])
        return recommendations

    def item_base_suggest(user_id):
        # 確認使用者有無按讚過
        sql_4_check = "SELECT * FROM pockets WHERE user_id = %s LIMIT 1"
        val_4_check = (user_id,)
        check_result = Database.read_one(sql_4_check, val_4_check)
        if (check_result is None):
            return False

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

        # 計算相似度，用google評分填充NaN值
        cosine_sim_df = calculate_cosine_similarity(pivot_table, google_rating_dict)
        
        # 推薦餐廳並用list儲存
        recommendations = recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants)
        return recommendations

