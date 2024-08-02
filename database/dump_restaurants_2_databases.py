import json
import re
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from dbconfig import Database

with open("data/NCKU_4km_unique_detail_0730.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

areas = ["東區", "中西區", "南區", "永康區", "北區"]
simplified_to_traditional = {
    "东区": "東區",
    "中西区": "中西區",
    "南区": "南區",
    "永康区": "永康區",
    "北区": "北區"
}
pattern = "|".join(areas + list(simplified_to_traditional.keys()))

for i in range(len(data)):
    
    google_rating = data[i].get("rating", None)
    google_rating_count = data[i].get("userRatingCount", None)
    takeout = data[i].get("takeout", None)
    dineIn = data[i].get("dineIn", None)
    delivery = data[i].get("delivery", None)
    reservable = data[i].get("reservable", None)
    
    ## 判斷行政區
    match = re.search(pattern, data[i]["formattedAddress"])
    if match:
        district = match.group()
        district = simplified_to_traditional.get(district, district)
    else:
        district = "未知"
    
    ## 判斷是否歇業
    businessStatus = 1 if data[i]["businessStatus"] == "OPERATIONAL" else 0;

    restaurant = {
        "name" : data[i]["displayName"]["text"],
        "place_id" : data[i]["id"],
        "address" : data[i]["formattedAddress"],
        "district" : district,
        "lat" : data[i]["location"]["latitude"],
        "lng" : data[i]["location"]["longitude"],
        "google_rating" : google_rating,
        "google_rating_count" : google_rating_count,
        "takeout" : takeout,
        "dineIn" : dineIn,
        "delivery" : delivery,
        "reservable" : reservable,
        "businessStatus" : businessStatus,
        "type" : data[i]["primaryType"],
    }
    sql = (
        "INSERT INTO restaurants (name, place_id, address, district, lat, lng, google_rating, google_rating_count, takeout, dineIn, delivery, reservable, businessStatus, type) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    val = (
        restaurant["name"],
        restaurant["place_id"],
        restaurant["address"],
        restaurant["district"],
        restaurant["lat"],
        restaurant["lng"],
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



