"""
네이버 맵의 데이터랩의 키워드 추출하기
"""
import os
import json
import time
import pandas as pd

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from find import *

load_dotenv()

URL = os.getenv("CRAWLING_URL")
SPOT_CSV_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/spots_for_crawling.csv"

# 원본 파일 불러오기
df = pd.read_csv(SPOT_CSV_PATH)

# 데이터랩의 키워드 가져오기
def get_naver_data(info):
    # 1. 크롬 옵션 객체 생성
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
    
    # 자동화 탐지 우회 옵션 추가
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 2. Service 객체를 통해 크롬 드라이버 실행
    service = Service(
        ChromeDriverManager().install()  # ChromeDriverManager를 사용하여 드라이버 자동 설치
    )
    driver = webdriver.Chrome(service=service, options=options)
    
    # 3. 메인 페이지로 이동하기
    if "인천" in info["name"]:
        driver.get(URL + info["name"])
    else:
        driver.get(URL + f"인천 {info['name']}")
    
    first_address = info["address"].split()[1]
    second_address = info["address"].split()[2]

    # 일단 주어진 기본 정보
    tel = info["tel"]
    homepage = info["homepage"]
    main_image = info["original_image"]
    overview = info["overview"]
    good_list = []

    time.sleep(10)

    # 해당 장소 찾기
    result = find_spot_button(driver, first_address, second_address, info)
    if result:
        # entryIframe으로 이동하기
        if result == 'next':
            # entryIframe이 없다면?
            if not is_entry_iframe(driver, info):
                return {"spot_code": info["spot_code"],
                        "tel": tel, 
                        "homepage": homepage, 
                        "original_image": main_image, 
                        "overview": overview, 
                        "good_points": good_list}
            else:
                print(f"{info['name']} - 정보를 찾을 수 있습니다.")

        # 특정 장소 정보 iframe으로 이동
        else:
            # 클릭
            result.click()
            time.sleep(5)
            # iframe 이동하지 못하면
            if is_entry_iframe(driver, info):
                print(f"{info['name']} - 정보를 찾을 수 있습니다.")
    
    # 이미지 정보가 없다면 정보 얻기
    if not main_image:
        main_image = find_image(driver, info)

    try:
        icons = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.O8qbU")))
        for icon in icons:
            icon_text = WebDriverWait(icon, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "strong.Aus_8 > span"))).text
            # 전화번호 정보 얻기
            if not tel:
                if icon_text == "전화번호":
                    tel = find_image(icon)

            # 홈페이지 주소 선택
            if not homepage:
                if icon_text == "홈페이지":
                    homepage = find_homepage(icon)

    except Exception as e:
        print(f"{info['name']} - 기본 정보 없음")
        
    try:
        tabs = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.tpj9w._tab-menu")))
        for tab in tabs:
            tab_name = tab.find_element(By.CSS_SELECTOR, "span.veBoZ").text
            
            # 정보 탭 선택해서 overview 찾기
            if not overview:
                if tab_name == "정보":
                    tab.click()
                    time.sleep(1)
                    # 정보 수집
                    overview = find_overview(driver)
                    break

    except Exception as e:
        print(f"{info['name']} - 개요가 존재하지 않습니다.")

    try:
        tabs = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.tpj9w._tab-menu")))
        for tab in tabs:
            tab_name = tab.find_element(By.CSS_SELECTOR, "span.veBoZ").text
            
            # 리뷰 수집
            if tab_name == "리뷰":
                tab.click()
                break
        
        time.sleep(10)

        # 이런 점이 좋았어요 찾기
        try:
            good_point_section = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.place_section.no_margin.ySHNE")))
            if good_point_section:
                title = WebDriverWait(good_point_section, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.place_section_header_title"))).text
                if "이런 점이 좋았어요" in title:
                    print("'이런 점이 좋았어요' 확인")
                    
                    find_additional_button(driver)

                    good_list = find_good_points(good_point_section, [], info)
        
        except Exception as e:
            print(f"{info['name']} - 이런 점이 좋았어요가 없습니다.")
    
    except Exception as e:
        print(f"{info['name']} - 리뷰 탭이 없습니다.")
    
    # 창 닫기
    driver.quit()
    
    return {"spot_code": info["spot_code"],
            "tel": tel, 
            "homepage": homepage, 
            "original_image": main_image, 
            "overview": overview, 
            "good_points": good_list}



# print(get_naver_data({
#         "name": "자유공원",
#         "address": "인천광역시 중구 제물량로232번길 46",
#         "mapx": "126.6222755091",
#         "mapy": "37.4752946269",
#         "tel": None,
#         "homepage": None,
#         "original_image": None,
#         "overview": None,
#     }))

all_naver_data = []

for idx, row in df.iterrows():
    info_dict = get_naver_data(row)
    all_naver_data.append(info_dict)

NAVER_JSON_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/naver_data.json"

if all_naver_data:
    with open(NAVER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_naver_data, f, ensure_ascii=False, indent=4)