import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# 기존 데이터 가져오기
SPOTS_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/total_info.json"
with open(SPOTS_JSON_PATH, "r", encoding="utf-8") as f:
    spots = json.load(f)

# 새로 저장할 CSV 경로
PREPROCESSED_DATA_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/spots.csv"

# 중첩된 dict를 평탄화(flatten)해서 CSV로 저장
flat_rows = []

for idx, value in spots.items():
    flat_rows.append(value)

df = pd.DataFrame(flat_rows)
df.to_csv(PREPROCESSED_DATA_PATH, index=False, encoding="utf-8-sig")