import os
import json
from dotenv import load_dotenv

load_dotenv()

SPOTS_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spots.json"
with open(SPOTS_JSON_PATH, "r", encoding="utf-8") as f:
    spots = json.load(f)

PREPROCESSED_DATA_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/spots.json"

for spot in spots:
    pass