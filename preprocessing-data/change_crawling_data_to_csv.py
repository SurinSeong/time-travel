import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# crawling_data = os.getenv("PREPROCESSED_DATA_PATH") + "/naver_data.json"
crawling_data = os.getenv("PREPROCESSED_DATA_PATH") + "/remain_naver_data.json"

with open(crawling_data, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

reviews = os.getenv("PREPROCESSED_DATA_PATH") + "/crawling_remain_reviews.csv"

df.to_csv(reviews, index=False, encoding="utf-8")

