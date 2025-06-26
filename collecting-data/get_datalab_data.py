"""
네이버 맵의 데이터랩의 키워드 추출하기
"""
import os
import json

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

URL = os.getenv("CRAWLING_URL")
SPOT_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/final_spot.json"

# 원본 파일 불러오기
with open(SPOT_JSON_PATH, "r", encoding="utf-8") as f:
    spots = json.load(f)

# 데이터랩의 키워드 가져오기
def get_naver_data(info):
    # 1. 크롬 옵션 객체 생성
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
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
    driver.get(URL + f"인천 {info["name"]}")
    
    # iframe 전환
    iframe_element = driver.find_element(By.ID, "searchIframe")
    driver.switch_to.frame(iframe_element)
    
    # 페이지 로딩 대기 + 항목 찾기
    spots = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li')))
    if spots:
        for spot in spots:
            button = spot.find_element(By.CSS_SELECTOR, "div.qbGlu > div.ouxiq > div.d7iiF > div > span.lWwyz > a")
            button.click()

            address = spot.find_element(By.CSS_SELECTOR, "div.qbGlu > div.ouxiq > div.d7iiF > div > div > div > div:nth-child(1) > span.hAvkz").text
            if address in info["address"]:      # 주소가 같다면 해당 장소라고 판단
                button = spot.find_element(By.CSS_SELECTOR, "div.qbGlu > div.ouxiq > div.ApCpt > a")
                button.click()      # 해당 장소 클릭
                break

    else:
        print(f"{info["name"]} - 해당 장소가 없습니다.")
        return None

    # iframe 전환
    iframe_element = driver.find_element(By.ID, "entryIframe")
    driver.switch_to.frame(iframe_element)

    # 혹시 모르는 AI 브리핑 내용 가져오기
    try:
        ai_title = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.place_section.no_margin.no_border._slog_visible.QIeE4 > h2 > div.place_section_header_title > strong"))).text
        if ai_title == "AI 브리핑":
            ai_briefs = driver.find_elements(By.CSS_SELECTOR, "div.place_section.no_margin.no_border._slog_visible.QIeE4 > div > ul > li")
            if ai_briefs:
                ai_content = []
                for ai_brief in ai_briefs:
                    ai_content.append(ai_brief.text)
                return ai_content
    except:
        print("해당 스팟에는 'AI 브리핑'이 존재하지 않습니다.")


    # 리뷰 탭 선택하기
    tabs = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#app-root > div > div > div.place_fixed_maintab > div > div > div > div > a")))
    
    if tabs:
        for tab in tabs:
            tab_name = tab.find_element(By.CSS_SELECTOR, "span.veBoZ")
            if tab_name == "리뷰":
                tab.click()
                break
    
    else:
        print(f"{info["name"]} - 해당 장소의 리뷰가 존재하지 않습니다.")
        return None

    keywords = []

    # 이런 점이 좋았어요 - 최대 10개 저장하기
    try:
        good_point_title = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.place_section.no_margin.ySHNE > h2.place_section_header > div.place_section_header_title")))
        if good_point_title.text == "이런 점이 좋았어요":
            try:
                button = driver.find_element(By.CSS_SELECTOR, "div.place_section.no_margin.ySHNE > div > div > div.mrSZf > div > a")
                while button:
                    button.click()
            except:
                print("바로 '이런점이 좋았어요'를 가져옵니다.")
            
            good_points = driver.find_elements(By.CSS_SELECTOR, "div.place_section.no_margin.ySHNE > div > div > div.mrSZf > ul > li")
            for good_point in good_points:
                good_point_content = good_point.find_element(By.CSS_SELECTOR, "div.vfTO3 > span.t3JSf").text
                good_point_number = good_point.find_element(By.CSS_SELECTOR, "div.vfTO3 > span.CUoLy").text
                keywords.append(f"{good_point_content} ({good_point_number})")
        else:
            print(f"{info["name"]} - 해당 장소에 대한 키워드를 추출할 수 없습니다. ")
            return None
    except:
        print(f"{info["name"]} - 해당 장소에 대한 키워드를 추출할 수 없습니다. ")
        return None
    
    # 창 닫기
    driver.quit()
    
    return keywords

# get_naver_data("인천 자유공원")

all_naver_data = {}

for spot in spots:
    spot_info = spots[spot]
    naver_data = get_naver_data(spot_info)
    if naver_data:
        all_naver_data[spot] = naver_data
    else:
        all_naver_data[spot] = None

NAVER_JSON_PATH = os.getenv("DATA_FOLDER_PATH") + "/naver_data.json"

if all_naver_data:
    with open(NAVER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_naver_data, f, ensure_ascii=False, indent=4)