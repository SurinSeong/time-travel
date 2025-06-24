import os
import json
from dotenv import load_dotenv

from find_base_code import get_incheon_tour_spot

load_dotenv()

mobile_os="WEB"    # IOS, AND, WEB
mobile_app="time-travel"
api_key = os.getenv("API_KEY")
data_folder_path = os.getenv("DATA_FOLDER_PATH")

CAT3_JSON_PATH = data_folder_path + "/cat3.json"
SPOT_JSON_PATH = data_folder_path + "/spots.json"

if os.path.exists(CAT3_JSON_PATH):
    with open(CAT3_JSON_PATH, "r", encoding="utf-8") as f:
        cat3_data = json.load(f)
        
spots = {}

for cat1_code in cat3_data:
    if cat1_code not in spots:
        spots[cat1_code] = {}
    
    for cat2_code in cat3_data[cat1_code]:
        if cat2_code not in spots[cat1_code]:
            spots[cat1_code][cat2_code] = {}
        
        for cat3_code in cat3_data[cat1_code][cat2_code]:
            if cat3_code not in spots[cat1_code][cat2_code]:
                spots[cat1_code][cat2_code][cat3_code] = {}
                
            tour_spots = get_incheon_tour_spot(mobile_os, mobile_app, api_key, cat1_code, cat2_code, cat3_code)
            if tour_spots:
                for spot in tour_spots:
                    spots[cat1_code][cat2_code][cat3_code][spot["contentid"]] = {
                        "cat1": cat1_code,
                        "cat2": cat2_code,
                        "cat3": cat3_code,
                        "name": spot["title"],
                        "address": spot["addr1"],
                        "mapx": spot["mapx"],
                        "mapy": spot["mapy"]
                    }
                
with open(SPOT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(spots, f, ensure_ascii=False, indent=4)