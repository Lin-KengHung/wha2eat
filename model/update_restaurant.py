import os
import sys
import requests
import threading
import time

from requests.exceptions import RequestException
from dotenv import load_dotenv
load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)
from dbconfig import Database


sql = "SELECT place_id, url FROM images LIMIT 1000;" 
image_data = Database.read_all(sql)




# 定義一個處理 URL 並檢查是否有效的函式
def check_urls(data_chunk, invalid_place_ids, invalid_urls):
    for item in data_chunk:
        place_id = item["place_id"]
        url = item["url"]
        try:
            response = requests.head(url, timeout=5)  # 設定超時 5 秒
            if response.status_code != 200:
                invalid_place_ids.add(place_id)
                invalid_urls.append(url)

        except RequestException:
            invalid_place_ids.add(place_id)
            invalid_urls.append(url)

# 使用多執行緒
def check_urls_multithreaded(data, num_threads=5):
    # 存放無效的 place_id與url
    invalid_place_ids = set()  
    invalid_urls = []
    valid_urls = []
    # 執行緒池，設定平均分配執行緒處理的數量
    threads = []
    chunk_size = len(data) // num_threads  

    # 創建執行緒與分配任務
    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = None if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=check_urls, args=(data[start_index:end_index], invalid_place_ids, invalid_urls))
        threads.append(thread)
        thread.start()

    # 等待所有執行緒完成任務
    for thread in threads:
        thread.join()

    return invalid_place_ids, invalid_urls

def get_valid_urls(data, invalid_place_ids, invalid_urls):
    valid_urls = []
    for image in data:
        if image["place_id"] in invalid_place_ids and image["url"] not in invalid_urls:
            valid_urls.append(image["url"])

    return valid_urls


invalid_place_ids, invalid_urls = check_urls_multithreaded(data=image_data, num_threads=10)
valid_urls = get_valid_urls(data=image_data, invalid_place_ids=invalid_place_ids, invalid_urls=invalid_urls)

# --------------------------------------------------------
# 打API
# --------------------------------------------------------

API_KEY = os.getenv("API_KEY")

def get_place_details(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    
    # 請求標頭
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'id,displayName,photos'  # 指定需要的欄位
    }
    
    # 請求參數，限制語言為繁體中文
    params = {
        'languageCode': 'zh-TW'
    }
    
    # 發送 GET 請求
    response = requests.get(url, headers=headers, params=params)
    
    # 檢查回應狀態
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for place_id {place_id}: {response.status_code}")
        return None

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
    return False

def update_problematic_restaurants(invalid_place_ids, valid_urls):
    if len(invalid_place_ids) == 0 :
        return "pass"
    results = []
    for place_id in invalid_place_ids:
        # 獲取餐廳詳細資料
        details = get_place_details(place_id)
        if details and 'photos' in details:
            photos = details['photos']
            for photo in photos:
                photo_name = photo['name']

                # 使用get_place_photo_url 獲取圖片的最終URL
                photo_url = get_place_photo_url(photo_name, API_KEY)
                if photo_url :
                    if photo_url not in valid_urls:
                        new_image_data = {
                            'place_id' : place_id,
                            'url' : photo_url
                        }
                        results.append(new_image_data)
                else:
                    print(f"Failed to fetch new photo for place_id {place_id}")
        else:
            print(f"No photos found for place_id {place_id}")

    return result

new_image_result = update_problematic_restaurants(invalid_place_ids= invalid_place_ids, valid_urls=valid_urls)

if (new_image_result == "pass"):
    print("沒有資料需要更新")
else:
    ## 刪除壞檔案
    for url in invalid_urls:
        sql = "DELETE FROM images where url = %s"
        val = (url,)
        result = Database.delete(sql, val)
        if (result):
            print("刪除成功")
        else:
            print("刪除失敗")
            print(url)


    ## 新增檔案
    for image in new_image_result:
        sql = "INSERT INTO images (place_id, url) VALUES (%s, %s)"
        val = (image["place_id"], image["url"])
        result = Database.update(sql, val)
        if (result):
            print("新增成功")
        else:
            print("新增失敗")
            print(image)

