"""
관광지에 대한 디테일한 정보 추출하기
=> 무조건 totalcount 정보 확인 후 가져오기
=> 저작권 표시해주기 (Type1 : 출처표시 권장)

- detailCommon2/    # 공통정보조회
    - 관광지에 대한 설명(overview), 홈페이지 주소(homepage), 전화번호(tel) 
    
- detailIntro2/    # 소개정보조회 - 수집 완
    - 유모차대여정보(chkbabycarriage), 신용카드가능정보(chkcreditcard), 애완동물동반가능정보(chkpet),
    세계문화유산유무(heritage1), 세계자연유산유무(heritage2), 세계기록유산유무(heritage3),
    개장일(opendate), 주차시설(parking), 쉬는날(restdate), 이용시기(useseason), 이용시간(usetime), 
    
- detailInfo2/    # 반복정보조회 - 수집 완
    - 정보명(infoname), 정보내용(infotext)
    
- detailImage2/    # 이미지정보조회 - 수집 완
    - originimgurl(원본이미지)
    
- detailPetTour2/    # 반려동물동반여행정보
    - 전부 필요하다고 생각됨.
"""

import os
import json
import requests
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
ENDPOINT = os.getenv("KORSERVICE2")
API_KEY = os.getenv("API_KEY")

# 관광지 contentid 받기
SPOT_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spots.json"
with open(SPOT_JSON_PATH, "r", encoding="utf-8") as f:
    spots = json.load(f)

# 상세 정보 받기 로직 구현

# 1. 공통 정보 조회
def get_common_info(content_id, mobile_os="WEB", mobile_app="time-travel"):
    # 공통 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailCommon2"
    params = {
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
        "serviceKey" : API_KEY,
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

    except Exception as e:
        print(f"[{content_id}] 첫 요청 JSON 파싱 실패:", e)
        print("응답 내용:", response.text)
        return None
    
    if "response" not in data or not data["response"]["body"]["totalCount"]:
        return None
    
    total_count = data["response"]["body"]["totalCount"]
    max_page_num = (total_count // 10) + (1 if total_count % 10 else 0)
    
    # 하나의 spot에 대한 공통 정보를 저장하기
    common_info = {}
    
    for n in range(1, max_page_num+1):
        params["pageNo"] = str(n)

        # 공통 정보 요청 URL
        try:
            response = requests.get(API_URL, params=params)
            page_data = response.json()
            items = page_data["response"]["body"]["items"]["item"]

            if not items:
                continue

            contents = items[0]

            for key in ["tel", "homepage", "overview"]:
                if key in contents:
                    if key not in common_info:
                        common_info[key] = contents[key]
                    elif common_info[key] != contents[key]:
                        common_info[key] += " " + contents[key]

        except Exception as e:
            print(f"[{content_id} - page {n}] ❌ JSON 파싱 실패:", e)
            print("응답 내용:", response.text[:300])
            continue

    return common_info

# 2. 반복 정보 조회
def get_repeat_info(content_id, mobile_os="WEB", mobile_app="time-travel"):
    # 반복 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailInfo2"
    params = {
        "serviceKey" : API_KEY,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
        "contentTypeId": "12",
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()
        print(data)

    except Exception as e:
        print(f"[{content_id}] 첫 요청 JSON 파싱 실패:", e)
        print("응답 내용:", response.text[:300])
        return None
    
    if "response" not in data or not data["response"]["body"]["totalCount"]:
        return None
    
    total_count = data["response"]["body"]["totalCount"]
    
    max_page_num = (total_count // 10) + (1 if total_count % 10 else 0)
    
    repeat_info = {}

    for n in range(1, max_page_num+1):
        params["pageNo"] = str(n)

        # 공통 정보 요청 URL
        try:
            response = requests.get(API_URL, params=params)
            page_data = response.json()
            items = page_data["response"]["body"]["items"]["item"]

            if not items:
                continue

            contents = items[0]

            for key in ["infoname", "infotext"]:
                if key in contents:
                    if key not in repeat_info:
                        repeat_info[key] = contents[key]
                    elif repeat_info[key] != contents[key]:
                        repeat_info[key] += " " + contents[key]

        except Exception as e:
            print(f"[{content_id} - page {n}] ❌ JSON 파싱 실패:", e)
            print("응답 내용:", response.text[:300])
            continue

    return repeat_info

# 3. 소개 정보 조회
def get_intro_info(content_id, mobile_os="WEB", mobile_app="time-travel"):
    # 소개 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailIntro2"
    params = {
        "serviceKey" : API_KEY,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
        "contentTypeId": "12",
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

    except Exception as e:
        print(f"[{content_id}] 첫 요청 JSON 파싱 실패:", e)
        print("응답 내용:", response.text[:300])
        return None
    
    if "response" not in data or not data["response"]["body"]["totalCount"]:
        return None
    
    total_count = data["response"]["body"]["totalCount"]
    
    max_page_num = (total_count // 10) + (1 if total_count % 10 else 0)
    
    intro_info = {}

    for n in range(1, max_page_num+1):
        params["pageNo"] = str(n)

        # 공통 정보 요청 URL
        try:
            response = requests.get(API_URL, params=params)
            page_data = response.json()
            items = page_data["response"]["body"]["items"]["item"]

            if not items:
                continue

            contents = items[0]
    
            for key in ["chkbabycarriage", "chkcreditcard", "chkpet", "heritage1", "heritage2", "heritage3", "opendate", "parking", "restdate", "useseason", "usetime"]:
                if key in contents:
                    if key not in intro_info:
                        intro_info[key] = contents[key]
                    elif intro_info[key] != contents[key]:
                        intro_info[key] += " " + contents[key]

        except Exception as e:
            print(f"[{content_id} - page {n}] ❌ JSON 파싱 실패:", e)
            print("응답 내용:", response.text[:300])
            continue

    return intro_info

# 4. 이미지 정보 조회
def get_image_info(content_id, mobile_os="WEB", mobile_app="time-travel"):
    # 소개 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailImage2"
    params = {
        "serviceKey" : API_KEY,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

    except Exception as e:
        print(f"[{content_id}] 첫 요청 JSON 파싱 실패:", e)
        print("응답 내용:", response.text[:300])
        return None
    
    if "response" not in data or not data["response"]["body"]["totalCount"]:
        return None
    
    total_count = data["response"]["body"]["totalCount"]
    
    max_page_num = (total_count // 10) + (1 if total_count % 10 else 0)
    
    image_info = {}

    for n in range(1, max_page_num+1):
        params["pageNo"] = str(n)

        # 이미지 정보 요청 URL
        try:
            response = requests.get(API_URL, params=params)
            page_data = response.json()
            items = page_data["response"]["body"]["items"]["item"]

            if not items:
                continue

            contents = items[0]
    
            for key in ["originimgurl", "smallimageurl"]:
                if key in contents:
                    if key not in image_info:
                        image_info[key] = contents[key]
                    elif image_info[key] != contents[key]:
                        image_info[key] += " " + contents[key]

        except Exception as e:
            print(f"[{content_id} - page {n}] ❌ JSON 파싱 실패:", e)
            print("응답 내용:", response.text[:300])
            continue

    return image_info

# 5. 반려동물 동반 여행 정보 조회
def get_pet_info(content_id, mobile_os="WEB", mobile_app="time-travel"):
    # 소개 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailPetTour2"
    params = {
        "serviceKey" : API_KEY,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

    except Exception as e:
        print(f"[{content_id}] 첫 요청 JSON 파싱 실패:", e)
        print("응답 내용:", response.text[:300])
        return None
    
    if "response" not in data or not data["response"]["body"]["totalCount"]:
        return None
    
    total_count = data["response"]["body"]["totalCount"]
    
    max_page_num = (total_count // 10) + (1 if total_count % 10 else 0)
    
    pet_info = {}

    for n in range(1, max_page_num+1):
        params["pageNo"] = str(n)

        # 이미지 정보 요청 URL
        try:
            response = requests.get(API_URL, params=params)
            page_data = response.json()
            items = page_data["response"]["body"]["items"]["item"]

            if not items:
                continue

            contents = items[0]
    
            for key in ["acmpyPsblCpam", "relaRntlPrdlst", "acmpyNeedMtr", "relaFrnshPrdlst", "etcAcmpyInfo", "relaPurcPrdlst", "relaAcdntRiskMtr", "relaPosesFclty"]:
                if key in contents:
                    if key not in pet_info:
                        pet_info[key] = contents[key]
                    elif pet_info[key] != contents[key]:
                        pet_info[key] += " " + contents[key]

        except Exception as e:
            print(f"[{content_id} - page {n}] ❌ JSON 파싱 실패:", e)
            print("응답 내용:", response.text[:300])
            continue

    return pet_info


print(len(spots))

all_common_info = {}
all_repeat_info = {}
all_intro_info = {}
all_image_info = {}
all_pet_info = {}

# test = get_common_info("1113230")
test = get_repeat_info("1113230")
# test = get_intro_info("1113230")
# test = get_image_info("1113230")
# test = get_pet_info("1113230")
print(test)

# for spot in spots:
#     print(spot)
    
#     # 공통 정보 저장
#     if spot not in all_common_info:
#         all_common_info[spot] = get_common_info(spot)

#     # 반복 정보 저장
#     if spot not in all_repeat_info:
#         all_repeat_info[spot] = get_repeat_info(spot)

#     # 소개 정보 저장
#     if spot not in all_intro_info:
#         all_intro_info[spot] = get_intro_info(spot)

#     # 이미지 정보 저장
#     if spot not in all_image_info:
#         all_image_info[spot] = get_image_info(spot)

#     # 반려동물 정보 저장
#     if spot not in all_pet_info:
#         all_pet_info[spot] = get_pet_info(spot)


# COMMON_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/common_info.json"
# REPEAT_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/repeat_info.json"
# INTRO_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/intro_info.json"
# IMAGE_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/image_info.json"
# PET_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/pet_info.json"

# if all_common_info:
#     with open(COMMON_JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_common_info, f, ensure_ascii=False, indent=4)

# if all_repeat_info:
#     with open(REPEAT_JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_repeat_info, f, ensure_ascii=False, indent=4)

# if all_intro_info:
#     with open(INTRO_JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_intro_info, f, ensure_ascii=False, indent=4)

# if all_image_info:
#     with open(IMAGE_JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_image_info, f, ensure_ascii=False, indent=4)

# if all_pet_info:
#     with open(PET_JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(all_pet_info, f, ensure_ascii=False, indent=4)