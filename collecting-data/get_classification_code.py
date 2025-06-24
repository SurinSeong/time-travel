import os
import json
from dotenv import load_dotenv

from find_base_code import get_service_code

load_dotenv()

mobile_os="WEB"    # IOS, AND, WEB
mobile_app="time-travel"
api_key = os.getenv("API_KEY")
data_folder_path = os.getenv("DATA_FOLDER_PATH")

CAT1_JSON_PATH = data_folder_path + "/cat1.json"
CAT2_JSON_PATH = data_folder_path + "/cat2.json"
CAT3_JSON_PATH = data_folder_path + "/cat3.json"

# cat1 분류 번호 저장하기
raw_cat1_data = get_service_code(mobile_os, mobile_app, api_key)
cat1_data = {entry["code"]: entry["name"] for entry in raw_cat1_data["item"]}
    
with open(CAT1_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cat1_data, f, ensure_ascii=False, indent=4)

# cat1을 바탕으로 cat2 분류 번호 저장하기
for cat1 in cat1_data:
    if os.path.exists(CAT2_JSON_PATH):
        with open(CAT2_JSON_PATH, "r", encoding="utf-8") as f:
            cat2_data = json.load(f)
            
        cat1_code = cat1
        raw_cat2_data = get_service_code(mobile_os, mobile_app, api_key, cat1_code)
        new_cat2_data = {cat1_code: {entry["code"]: entry["name"] for entry in raw_cat2_data["item"]}}
        
        cat2_data.update(new_cat2_data)
        
        with open(CAT2_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(cat2_data, f, ensure_ascii=False, indent=4)
            
    else:
        cat1_code = cat1
        raw_cat2_data = get_service_code(mobile_os, mobile_app, api_key, cat1_code)
        cat2_data = {cat1_code: {entry["code"]: entry["name"] for entry in raw_cat2_data["item"]}}
        
        with open(CAT2_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(cat2_data, f, ensure_ascii=False, indent=4)
        
# cat2를 바탕으로 cat3 분류 번호 저장하기
if os.path.exists(CAT3_JSON_PATH):
    with open(CAT3_JSON_PATH, "r", encoding="utf-8") as f:
        cat3_data = json.load(f)
else:
    cat3_data = {}

for cat1_code in cat2_data:
    if cat1_code not in cat3_data:
        cat3_data[cat1_code] = {}
        
    for cat2_code in cat2_data[cat1_code]:
        
        raw_cat3_data = get_service_code(mobile_os, mobile_app, api_key, cat1_code, cat2_code)
        cat3_data[cat1_code][cat2_code] = {
            entry["code"]: entry["name"] for entry in raw_cat3_data["item"]
        }
        
with open(CAT3_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cat3_data, f, ensure_ascii=False, indent=4)
                