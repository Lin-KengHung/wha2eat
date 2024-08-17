import json

# 读取原始 JSON 数据文件
with open('小樹屋半徑2km_rawdata_0815.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 初始化一个空的字典来存储唯一的地方
unique_places_dict = {}

# 初始化一个空的列表来存储餐厅名称
restaurant_names = []

# 遍历所有获取到的地方数据
for place in data:
    place_id = place['id']  # 获取地方的ID
    if place_id not in unique_places_dict:
        unique_places_dict[place_id] = place  # 如果ID不在字典中，则加入字典
        # 获取餐厅名称并加入列表
        if 'displayName' in place and 'text' in place['displayName']:
            restaurant_names.append(place['displayName']['text'])

# 从字典的值中获取唯一的地方列表
unique_places = list(unique_places_dict.values())

# 记录去重后的餐厅数量
total_restaurants = len(unique_places)
print(f"Total unique restaurants: {total_restaurants}")

# 保存去重后的 JSON 数据文件
with open('小樹屋2km_unique_detail_0815.json', 'w', encoding='utf-8') as f:
    json.dump(unique_places, f, ensure_ascii=False, indent=2)

# 保存餐厅名称到文本文件
with open('小樹屋餐廳名稱_0815.txt', 'w', encoding='utf-8') as f:
    for name in restaurant_names:
        f.write(name + '\n')

print("去重后的 JSON 数据和餐厅名称列表已生成。")
