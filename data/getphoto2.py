import requests
import json
import time
import os
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_KEY")

# 打 place photo API 的邏輯
def get_place_photo_url(photo_name, api_key, retries=3, delay=1):
    url = f'https://places.googleapis.com/v1/{photo_name}/media?maxHeightPx=600&maxWidthPx=800&key={api_key}'
    
    # 避免打API速度太快而失敗
    for attempt in range(retries):
        response = requests.get(url, allow_redirects=False)
        if response.status_code == 302:
            photo_url = response.headers['Location']
            return photo_url
        else:
            print(f"Attempt {attempt + 1} failed to fetch photo URL for {photo_name}, status code: {response.status_code}")
            if attempt < retries - 1:
                time.sleep(delay)  
    print(f"Failed to fetch photo URL for {photo_name} after {retries} attempts")
    return None

# 取出每個餐廳的給的photo place_name，打API，處裡數據
def process_places_data(places_data, api_key):
    results = []
    
    for place in places_data:
        place_id = place['id']
        display_name = place['displayName']['text']
        photo_urls = []
        
        if 'photos' in place:
            photos = place['photos']
            for photo in photos[:4]:  
                photo_name = photo['name']
                photo_url = get_place_photo_url(photo_name, api_key)
                if photo_url:
                    photo_urls.append(photo_url)
                time.sleep(1)  
        
        results.append({
            'id': place_id,
            'displayName': display_name,
            'photoUrls': photo_urls
        })
    
    return results

# 讀檔案，將資料儲存到json檔案
with open('小樹屋2km_unique_detail_0815.json', 'r', encoding='utf-8') as f:
    places_data = json.load(f)

processed_data = process_places_data(places_data, API_KEY)

with open('小樹屋2km_photo_0815', 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=2)

print("Processed data has been saved.")
