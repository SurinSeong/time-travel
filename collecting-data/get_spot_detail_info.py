"""
관광지에 대한 디테일한 정보 추출하기
=> 무조건 totalcount 정보 확인 후 가져오기
=> 저작권 표시해주기 (Type1 : 출처표시 권장)

- detailCommon2/    # 공통정보조회
    - 관광지에 대한 설명(overview), 홈페이지 주소(homepage), 전화번호(tel) 
    
- detailIntro2/    # 소개정보조회
    - 유모차대여정보(chkbabycarriage), 신용카드가능정보(chkcreditcard), 애완동물동반가능정보(chkpet),
    세계문화유산유무(heritage1), 세계자연유산유무(heritage2), 세계기록유산유무(heritage3),
    개장일(opendate), 주차시설(parking), 쉬는날(restdate), 이용시기(useseason), 이용시간(usetime), 
    
- detailInfo2/    # 반복정보조회
    - 정보명(infoname), 정보내용(infotext)
    
- detailImage2/    # 이미지정보조회
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
mobile_os="WEB"
mobile_app="time-travel"
api_key = os.getenv("API_KEY")

# 관광지 contentid 받기


# 상세 정보 받기
def get_detail_info(content_id):
    # 공통 정보 요청 URL
    API_URL = BASE_URL + ENDPOINT + "detailCommon2"
    params = {
        "serviceKey" : api_key,
        "MobileOS": mobile_os,
        "MobileApp": mobile_app,
        "_type": "json",
        "contentId": content_id,
    }
    
    response = requests.get(API_URL, params=params).json()
    
    max_spot_num = response["response"]["body"]["totalCount"]
    
    if max_spot_num == 0:
        return None
    
    if max_spot_num % 10 != 0:
        max_page_num = max_spot_num // 10 + 1
    else:
        max_page_num = max_spot_num // 10
        
    pass