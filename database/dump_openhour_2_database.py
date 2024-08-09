import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from dbconfig import Database

with open("data/NCKU_4km_unique_detail_0730.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

count =0;
for i in range(len(data)):
    if "regularOpeningHours" in data[i]:
        periods = data[i]["regularOpeningHours"]["periods"]
        sql = ("INSERT INTO opening_hours (place_id, day_of_week, open_time, close_time) "
                "VALUES (%s, %s, %s, %s)"
        )
        for period in periods:
            if "close" in period:
                times = [period["open"]["hour"], period["open"]["minute"], period["close"]["hour"], period["close"]["minute"]]
                times = list(map(lambda time: f"0{time}" if time < 10 else str(time), times))
                if period["open"]["day"] == period["close"]["day"]:
                    open_time = f"{times[0]}:{times[1]}:00"
                    close_time = f"{times[2]}:{times[3]}:00"
                    val = (data[i]["id"], period["open"]["day"], open_time, close_time)
                    Database.update(sql, val)
                else: # 過夜營業的情況
                    # 過夜前營業時間
                    open_time = f"{times[0]}:{times[1]}:00"
                    close_time = "24:00:00"
                    val = (data[i]["id"], period["open"]["day"], open_time, close_time)
                    Database.update(sql, val)
                    # 過夜後營業時間
                    open_time = "00:00:00"
                    close_time = f"{times[2]}:{times[3]}:00"
                    val = (data[i]["id"], period["close"]["day"], open_time, close_time)
                    Database.update(sql, val)
            else: # 24小時營業
                for j in range(7):
                    val = (data[i]["id"], j, "00:00:00", "24:00:00")
                    Database.update(sql, val)
