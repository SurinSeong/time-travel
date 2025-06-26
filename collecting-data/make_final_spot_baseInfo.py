import os
import json
from dotenv import load_dotenv

load_dotenv()

SPOT_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/spots.json"

# 원본 파일 불러오기
with open(SPOT_JSON_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 관광지 코드와 기본 정보만 추출
def extract_spots(node, result):
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, dict) and all(k in value for k in ("cat1", "cat2", "cat3", "name", "address", "mapx", "mapy")):
                result[key] = {
                    "cat1": value["cat1"],
                    "cat2": value["cat2"],
                    "cat3": value["cat3"],
                    "name": value["name"],
                    "address": value["address"],
                    "mapx": value["mapx"],
                    "mapy": value["mapy"]
                }
            else:
                extract_spots(value, result)

# 결과 저장 딕셔너리
final_data = {}
extract_spots(raw_data, final_data)

FINAL_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spots.json"

# 결과 파일 저장
with open(FINAL_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)