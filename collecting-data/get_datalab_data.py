"""
네이버 맵의 데이터랩의 키워드 추출하기
"""
import os
import time

from dotenv import load_dotenv
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

URL = os.getenv("CRAWLING_URL")

def get_datalab_data(keyword):
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
    driver.get(URL + keyword)
    
    # iframe 전환
    iframe_element = driver.find_element(By.ID, "searchIframe")
    driver.switch_to.frame(iframe_element)
    
    # 페이지 로딩 대기 + 항목 찾기
    spots = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li')))
    if spots:
        print(len(spots))
    # time.sleep(2)
    
    
    
    # 창 닫기
    driver.quit()
    
    pass

get_datalab_data("인천 자유공원")