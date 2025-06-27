import os
import json
from dotenv import load_dotenv

load_dotenv()

BASIC_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spots.json"
COMMON_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/common_info.json"
INTRO_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/intro_info.json"
REPEAT_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/repeat_info.json"
IMAGE_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/image_info.json"
PET_INFO_PATH = os.getenv("DATA_FOLDER_PATH") + "/pet_info.json"

# 서비스 분류 체계 코드 정보
CAT1_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/cat1.json"
CAT2_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/cat2.json"
CAT3_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/cat3.json"

# JSON 파일 불러오기
with open(BASIC_INFO_PATH, "r", encoding="utf-8") as f:
    basic_info = json.load(f)

with open(COMMON_INFO_PATH, "r", encoding="utf-8") as f:
    common_info = json.load(f)

with open(INTRO_INFO_PATH, "r", encoding="utf-8") as f:
    intro_info = json.load(f)

with open(REPEAT_INFO_PATH, "r", encoding="utf-8") as f:
    repeat_info = json.load(f)

with open(IMAGE_INFO_PATH, "r", encoding="utf-8") as f:
    image_info = json.load(f)

with open(PET_INFO_PATH, "r", encoding="utf-8") as f:
    pet_info = json.load(f)

with open(CAT1_JSON_PATH, "r", encoding="utf-8") as f:
    CAT1_INFO = json.load(f)

with open(CAT2_JSON_PATH, "r", encoding="utf-8") as f:
    CAT2_INFO = json.load(f)

with open(CAT3_JSON_PATH, "r", encoding="utf-8") as f:
    CAT3_INFO = json.load(f)


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

            elif key == "cat3":
                new_key_name = "small_category"
                new_data = CAT3_INFO[data[key]]
                info[new_key_name] = new_data

            else:
                info[key] = data[key]
    
    # 공통 정보


    # 소개 정보


    # 반복 정보


    # 이미지 정보


    # 반려동물 정보
    return info


# 하나의 장소에 대한 정보 합치는 함수
def concat_all_data(spot_code):
    info = {}

    # 기본 정보에 대한 컬럼 정보 넣어주기
    for key in basic_info[spot_code]:
        pass

    return info

all_data = {}

for i, spot_code in enumerate(basic_info, 1):
    # print(i, spot_code)
    all_data[i] = concat_all_data(spot_code)