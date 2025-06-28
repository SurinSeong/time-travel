import os
import json
from dotenv import load_dotenv

load_dotenv()

BASIC_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spots.json"
COMMON_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/common_info.json"
IMAGE_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/image_info.json"
TOTAL_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/total_info.json"

# 서비스 분류 체계 코드 정보
CAT1_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/cat1.json"
CAT2_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/cat2.json"

# JSON 파일 불러오기
with open(BASIC_INFO_PATH, "r", encoding="utf-8") as f:
    basic_info = json.load(f)

with open(COMMON_INFO_PATH, "r", encoding="utf-8") as f:
    common_info = json.load(f)

with open(IMAGE_INFO_PATH, "r", encoding="utf-8") as f:
    image_info = json.load(f)

with open(CAT1_JSON_PATH, "r", encoding="utf-8") as f:
    CAT1_INFO = json.load(f)

with open(CAT2_JSON_PATH, "r", encoding="utf-8") as f:
    CAT2_INFO = json.load(f)


INFO_DICT = {
    "basic": basic_info,
    "common": common_info,
    "image": image_info
}

# 컬럼명 변경하는 함수
def change_column_name(category, data):
    info = {}

    # 기본 정보
    if category == "basic":
        for key in data:
            if key == "cat1":
                new_key_name = "big_category"
                new_data = CAT1_INFO[data[key]]
                info[new_key_name] = new_data
            
            elif key == "cat2":
                new_key_name = "middle_category"
                new_data = CAT2_INFO[data[key]]
                info[new_key_name] = new_data

            elif key in ["name", "address", "mapx", "mapy"]:
                info[key] = data[key]
    
    # 공통 정보
    if category == "common":
        if data:
            for key in data:
                info[key] = data[key]
        else:
            for key in ["tel", "homepage", "overview"]:
                info[key] = None

    # 이미지 정보
    if category == "image":
        if data:
            for key in data:
                if key == "originimgurl":
                    images = data[key].split()
                    new_key_name = "original_image"
                    info[new_key_name] = images[0]
        else:
            info["original_image"] = None

    return info


# 하나의 장소에 대한 정보 합치는 함수
def concat_all_data(spot_code):
    all_info = {"spot_code": spot_code}       # 하나의 장소에 대한 정보

    for category, data in INFO_DICT.items():
        info = change_column_name(category, data[spot_code])
        all_info.update(info)

    return all_info

# print(concat_all_data("1113230"))


# 모든 장소에 대한 정보
all_spots = {}

for i, spot_code in enumerate(basic_info, 1):
    # print(i, spot_code)
    all_spots[i] = concat_all_data(spot_code)


# 정보 저장하기
with open(TOTAL_INFO_PATH, "w", encoding="utf-8") as f:
    json.dump(all_spots, f, ensure_ascii=False, indent=4)