"""
네이버 맵의 데이터랩의 키워드 추출하기
"""
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

def get_datalab_data(keyword):
    # 1. 메인 페이지
    
    # 2. 크롬 옵션 객체 생성
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
    
    # 자동화 탐지 우회 옵션 추가
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("disable-blink-features=AutomationControlled")
    
    # 3. Service 객체를 통해 크롬 드라이버 실행
    service = Service(
        ChromeDriverManager().install()  # ChromeDriverManager를 사용하여 드라이버 자동 설치
    )
    driver = webdriver.Chrome(service=service, options=options)
    
    # 4. 메인 페이지로 이동하기
    
    # 페이지 로딩 대기하기
    time.sleep(3)
    
    # 5. 검색창 찾기
    
    pass