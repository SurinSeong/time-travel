import os
import requests
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
ENDPOINT = os.getenv("KORSERVICE2")

# 지역코드 불러오기
def get_area_code(mobile_os, mobile_app, api_key):
    # 요청 URL
    API_URL = BASE_URL + ENDPOINT + "areaCode2"
    params = {
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "serviceKey": api_key,
        "_type": "json",
    }
    
    response = requests.get(API_URL, params=params).json()
    
    return response

# 인천 : 2

# 서비스 분류 코드 불러오기
def get_service_code(mobile_os, mobile_app, api_key):
    # 요청 URL
    API_URL = BASE_URL + ENDPOINT + "categoryCode2"
    params = {
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "ContentTypeId": "12",    # 관광 타입 설정
        "cat1": "A02",
        "serviceKey": api_key,
        "_type": "json",
    }
    
    response = requests.get(API_URL, params=params).json()
    
    return response

# 인문(문화/예술/역사) : A02
# 역사 관광지 : A0201

# 분류체계 코드 목록
def get_big_classification_code(mobile_os, mobile_app, api_key):
    # 요청 URL
    API_URL = BASE_URL + ENDPOINT + "lclsSystmCode2"
    params = {
        "serviceKey" : api_key,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
    }
    
    response = requests.get(API_URL, params=params).json()
    
    return response

# 역사 관광 : HS

# 지역 기반 관광정보조회
def get_incheon_history_tour_spot(mobile_os, mobile_app, api_key):
    # 요청 URL
    API_URL = BASE_URL + ENDPOINT + "areaBasedList2"
    params = {
        "serviceKey" : api_key,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentTypeId": "12",
        "areaCode": "2",
        "cat1": "A02",
        "cat2": "A0201",
    }
    
    response = requests.get(API_URL, params=params).json()
    
    max_spot_num = response["response"]["body"]["totalCount"]
    print(max_spot_num)
    
    if max_spot_num % 10 != 0:
        max_page_num = max_spot_num // 10 + 1
    else:
        max_page_num = max_spot_num // 10
    
    history_spots = []
        
    for n in range(1, max_page_num+1):
        # 요청 URL
        API_URL = BASE_URL + ENDPOINT + "areaBasedList2"
        params = {
            "pageNo": str(n),
            "serviceKey" : api_key,
            "MobileOS": mobile_os,
            "MobileApp": mobile_app,
            "_type": "json",
            "contentTypeId": "12",
            "areaCode": "2",
            "cat1": "A02",
            "cat2": "A0201",
        }
        
        response = requests.get(API_URL, params=params).json()
        
        spots = response["response"]["body"]["items"]["item"]
        
        for spot in spots:
            history_spots.append(spot)
    
    return history_spots
    

mobile_os="WEB"
mobile_app="time-traveler"
api_key = os.getenv("API_KEY")

# print(get_incheon_history_tour_spot(mobile_os, mobile_app, api_key))
print(get_service_code(mobile_os, mobile_app, api_key))