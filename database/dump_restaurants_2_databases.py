import json
import re
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from dbconfig import Database

with open("data/小樹屋2km_unique_detail_0815.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

test_set = set()
type_translation = {
    'barbecue_restaurant': 'BBQ',
    'french_restaurant': '法式餐廳',
    'ramen_restaurant': '拉麵',
    'restaurant': '餐廳',
    'thai_restaurant': '泰式餐廳',
    'vegetarian_restaurant': '素食餐廳',
    'indian_restaurant': '印度餐廳',
    'korean_restaurant': '韓式餐廳',
    'bar': '餐酒館',
    'italian_restaurant': '義大利餐廳',
    'sushi_restaurant': '壽司',
    'indonesian_restaurant': '印尼餐廳',
    'fast_food_restaurant': '速食',
    'steak_house': '牛排館',
    'seafood_restaurant': '海鮮餐廳',
    'spanish_restaurant': '西班牙餐廳',
    'mexican_restaurant': '墨西哥餐廳',
    'hamburger_restaurant': '漢堡餐廳',
    'japanese_restaurant': '日式餐廳',
    'breakfast_restaurant': '早餐店',
    'vietnamese_restaurant': '越南餐廳',
    'chinese_restaurant': '中式餐廳',
    'american_restaurant': '美式餐廳',
    'meal_takeaway': '外賣',
    'middle_eastern_restaurant': '中東餐廳',
    'brunch_restaurant': '早午餐',
    'turkish_restaurant': '土耳其餐廳',
    'sandwich_shop': '三明治店',
    'pizza_restaurant': '披薩',
    'vegan_restaurant': '素食餐廳',
    'mediterranean_restaurant': '地中海餐廳',
    'brazilian_restaurant': '巴西餐廳'
}

for i in range(len(data)):

    google_rating = data[i].get("rating", None)
    google_rating_count = data[i].get("userRatingCount", None)
    takeout = data[i].get("takeout", None)
    dineIn = data[i].get("dineIn", None)
    delivery = data[i].get("delivery", None)
    reservable = data[i].get("reservable", None)

    # ## 判斷行政區
    # match = re.search(pattern, data[i]["formattedAddress"])
    # if match:
    #     district = match.group()
    #     district = simplified_to_traditional.get(district, district)
    # else:
    #     district = "未知"
    
    ## 判斷是否歇業
    businessStatus = 1 if data[i]["businessStatus"] == "OPERATIONAL" else 0;
    
    ## 餐廳類型中文轉換
    restaurant_type = type_translation[data[i]["primaryType"]] 

    restaurant = {
        "name": data[i]["displayName"]["text"],
        "place_id": data[i]["id"],
        "address": data[i]["formattedAddress"],
        "lat": data[i]["location"]["latitude"],
        "lng": data[i]["location"]["longitude"],
        "google_rating": google_rating,
        "google_rating_count": google_rating_count,
        "takeout": takeout,
        "dineIn": dineIn,
        "delivery": delivery,
        "reservable": reservable,
        "businessStatus": businessStatus,
        "type": restaurant_type,
    }
    sql = (
        "INSERT INTO restaurants (name, place_id, address, coordinates, google_rating, google_rating_count, takeout, dineIn, delivery, reservable, businessStatus, type) "
        "VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)'), %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    val = (
        restaurant["name"],
        restaurant["place_id"],
        restaurant["address"],
        restaurant["lng"],  # 經度
        restaurant["lat"],  # 緯度
        restaurant["google_rating"],
        restaurant["google_rating_count"],
        restaurant["takeout"],
        restaurant["dineIn"],
        restaurant["delivery"],
        restaurant["reservable"],
        restaurant["businessStatus"],
        restaurant["type"]
    )
    result = Database.update(sql, val)
    if result == 0:
        print(f'失敗！{restaurant["name"]}，{restaurant["place_id"]}')

