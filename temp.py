from Engine.map import Map
import json
with open("Resources/other/map_pools.json","r") as f:
    room_distrib=json.loads(f.read())["Basic"]
Map(25,0.9,0.02,room_distrib)