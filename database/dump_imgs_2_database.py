import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from dbconfig import Database

with open("data/NCKU_4km_photo_0801.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

sql = ("INSERT INTO images (place_id, url) "
        "VALUES (%s, %s)")

for i in range(len(data)):
    for j in range(len(data[i]["photoUrls"])):
        val = (data[i]["id"], data[i]["photoUrls"][j])
        Database.update(sql, val)

print("finished")