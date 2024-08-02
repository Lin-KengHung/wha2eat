import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from dbconfig import Database

with open("data/NCKU_4km_unique_detail_0730.json", mode="r", encoding="utf-8") as file:
    data = json.load(file)

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
                open_time = f"{times[0]}:{times[1]}:00"
                close_time = f"{times[2]}:{times[3]}:00"
                val = (data[i]["id"], period["open"]["day"], open_time, close_time)
                Database.update(sql, val)

            else: 
                for i in range(7):
                    val = (data[i]["id"], i, "00:00:00", "00:00:00")
                    Database.update(sql, val)
