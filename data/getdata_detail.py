import requests
import json
import math
import time
import os
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_KEY")
base_url = 'https://places.googleapis.com/v1/places:searchNearby'

def calculate_new_position(lat, lon, distance, bearing):
    R = 6371  # 地球半徑，單位公里
    lat_rad = math.radians(lat)  # 將緯度轉換為弧度
    lon_rad = math.radians(lon)  # 將經度轉換為弧度
    bearing_rad = math.radians(bearing)  # 將方位角轉換為弧度

    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) + 
                            math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad))
    new_lon_rad = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
                                       math.cos(distance / R) - math.sin(lat_rad) * math.sin(new_lat_rad))

    new_lat = math.degrees(new_lat_rad)  # 將新緯度轉換為度數
    new_lon = math.degrees(new_lon_rad)  # 將新經度轉換為度數
    return new_lat, new_lon

# 打 google place nearby search API
def fetch_places(center, radius, api_key):
    url = base_url
    payload = {
        "maxResultCount": 20,
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": center[0],
                    "longitude": center[1]
                },
                "radius": radius * 1000  
            }
        },
        "includedPrimaryTypes": ["restaurant"],
        "languageCode": "zh-TW"
    }
    fields = [
        "places.displayName",
        "places.businessStatus",
        "places.id",
        "places.photos",
        "places.primaryType",
        "places.location",
        "places.formattedAddress",
        "places.delivery",
        "places.dineIn",
        "places.takeout",
        "places.rating",
        "places.regularOpeningHours",
        "places.reservable",
        "places.userRatingCount"
    ]
    fieldMask = ",".join(fields)

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': fieldMask
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if 'places' in data:
        return data['places']
    else:
        return []

# 中心點經緯度
center_lat = 25.06254584380315
center_lon = 121.5217166283348
search_radius = 0.072  # 半徑設置為72m

grid_length = 4  # 總範圍為4000m * 4000m 正方形
step = 0.1  # 每100m一個點

# 生成範圍內的所有點的經緯度
points = []
num_steps = int(grid_length / step / 2)
for i in range(-num_steps, num_steps + 1):
    for j in range(-num_steps, num_steps + 1):
        new_lat, new_lon = calculate_new_position(center_lat, center_lon, step * i, 0)
        new_lat, new_lon = calculate_new_position(new_lat, new_lon, step * j, 90)
        points.append((new_lat, new_lon))

# 所有餐廳與所有經緯度座標打到餐廳的數量
all_places = []
api_call_info = []

for pos in points:
    places = fetch_places(pos, search_radius, API_KEY)
    all_places.extend(places)
    api_call_info.append({
        "latitude": pos[0],
        "longitude": pos[1],
        "result_count": len(places)
    })
    time.sleep(1)

# 輸出抓取到的總餐廳數量
total_restaurants = len(all_places)
print(f"Total restaurants fetched: {total_restaurants}")

# 儲存所有餐廳結果
with open('小樹屋半徑2km_rawdata_0815.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_places), f, ensure_ascii=False, indent=2)

# 儲存每個經緯度打到餐廳的數量
with open('小樹屋半徑2km_經緯度座標餐廳數量_0815.json', 'w', encoding='utf-8') as f:
    json.dump(api_call_info, f, ensure_ascii=False, indent=2)
