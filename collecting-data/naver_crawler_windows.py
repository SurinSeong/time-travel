"""
네이버 맵의 데이터랩의 키워드 추출하기 (Playwright 버전)
"""
import os
import json
import time
import pandas as pd
import asyncio

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from find_playwright import *

load_dotenv()

URL = os.getenv("CRAWLING_URL")
SPOT_CSV_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/incheon_463.csv"

# 원본 파일 불러오기
df = pd.read_csv(SPOT_CSV_PATH)

# 데이터랩의 키워드 가져오기
async def get_naver_data(info):
    async with async_playwright() as p:
        # 브라우저 실행 (headless=False로 설정하면 브라우저 창이 보임)
        browser = await p.chromium.launch(
            headless=False,  # True로 바꾸면 백그라운드 실행
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # 새 페이지 생성
        page = await browser.new_page()

        # 페이지 줌을 80%로 설정
        await page.evaluate("document.body.style.zoom = '0.80'")
        
        # # User-Agent 설정
        # await page.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # 자동화 탐지 우회
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 메인 페이지로 이동
        if "인천" in info["title"]:
            await page.goto(URL + info["title"])
        else:
            await page.goto(URL + f"인천 {info['title']}")
        
        first_address = info["addr1"].split()[1]
        second_address = info["addr1"].split()[2]

        # 일단 주어진 기본 정보
        tel = info.get("tel", None)
        homepage = info.get("homepage", None)
        main_image = info.get("firstimage", None)
        overview = info.get("overview", None)
        good_list = []

        await page.wait_for_timeout(8000)  # 8초 대기

        # 해당 장소 찾기
        result = await find_spot_button_playwright(page, first_address, second_address, info)
        if result:
            # entryIframe으로 이동하기
            if result == 'next':
                # entryIframe이 없다면?
                if not await is_entry_iframe_playwright(page, info):
                    await browser.close()
                    return {"spot_code": info["contentid"],
                            "tel": tel, 
                            "homepage": homepage, 
                            "original_image": main_image, 
                            "overview": overview, 
                            "good_points": good_list}
                else:
                    print(f"{info['title']} - 정보를 찾을 수 있습니다.")

            # 특정 장소 정보 iframe으로 이동
            else:
                # 클릭
                await result.click()
                await page.wait_for_timeout(5000)
                # iframe 이동하지 못하면
                if await is_entry_iframe_playwright(page, info):
                    print(f"{info['title']} - 정보를 찾을 수 있습니다.")
        
        # 이미지 정보가 없다면 정보 얻기
        if not main_image:
            main_image = await find_image_playwright(page, info)

        try:
            icons = await page.query_selector_all("div.O8qbU")
            for icon in icons:
                icon_text_element = await icon.query_selector("strong.Aus_8 > span")
                if icon_text_element:
                    icon_text = await icon_text_element.text_content()
                    
                    # 전화번호 정보 얻기
                    if not tel:
                        if icon_text == "전화번호":
                            tel = await find_tel_playwright(icon)

                    # 홈페이지 주소 선택
                    if not homepage:
                        if icon_text == "홈페이지":
                            homepage = await find_homepage_playwright(icon)

        except Exception as e:
            print(f"{info['title']} - 기본 정보 없음")
            
        try:
            tabs = await page.query_selector_all("a.tpj9w._tab-menu")
            for tab in tabs:
                tab_name_element = await tab.query_selector("span.veBoZ")
                if tab_name_element:
                    tab_name = await tab_name_element.text_content()
                    
                    # 정보 탭 선택해서 overview 찾기
                    if not overview:
                        if tab_name == "정보":
                            await tab.click()
                            await page.wait_for_timeout(1000)
                            # 정보 수집
                            overview = await find_overview_playwright(page)
                            break

        except Exception as e:
            print(f"{info['title']} - 개요가 존재하지 않습니다.")

        try:
            tabs = await page.query_selector_all("a.tpj9w._tab-menu")
            for tab in tabs:
                tab_name_element = await tab.query_selector("span.veBoZ")
                if tab_name_element:
                    tab_name = await tab_name_element.text_content()
                    
                    # 리뷰 수집
                    if tab_name == "리뷰":
                        print("리뷰 탭을 찾았습니다.")
                        await tab.click()
                        break
            
            await page.wait_for_timeout(10000)

            # 이런 점이 좋았어요 찾기
            try:
                good_point_section = await page.query_selector("div.place_section.no_margin.ySHNE")
                if good_point_section:
                    title_element = await good_point_section.query_selector("div.place_section_header_title")
                    if title_element:
                        title = await title_element.text_content()
                        if "이런 점이 좋았어요" in title:
                            print("'이런 점이 좋았어요' 확인")
                            
                            await find_additional_button_playwright(page)
                            good_list = await find_good_points_playwright(good_point_section, [], info)
            
            except Exception as e:
                print(f"{info['title']} - 이런 점이 좋았어요가 없습니다.")
        
        except Exception as e:
            print(f"{info['title']} - 리뷰 탭이 없습니다.")
        
        # 브라우저 닫기
        await browser.close()
        
        return {"spot_code": info["contentid"],
                "tel": tel, 
                "homepage": homepage, 
                "original_image": main_image, 
                "overview": overview, 
                "good_points": good_list}

# 동기 함수로 래핑
def get_naver_data_sync(info):
    return asyncio.run(get_naver_data(info))

# 테스트용 주석
# print(get_naver_data_sync({
#         "name": "자유공원",
#         "address": "인천광역시 중구 제물량로232번길 46",
#         "mapx": "126.6222755091",
#         "mapy": "37.4752946269",
#         "tel": None,
#         "homepage": None,
#         "original_image": None,
#         "overview": None,
#     }))

async def main():
    all_naver_data = []
    
    for idx, row in df.iterrows():
        info_dict = await get_naver_data(row)
        all_naver_data.append(info_dict)
    
    NAVER_JSON_PATH = os.getenv("PREPROCESSED_DATA_PATH") + "/naver_data_with_playwright.json"
    
    if all_naver_data:
        with open(NAVER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(all_naver_data, f, ensure_ascii=False, indent=4)

# 실행
if __name__ == "__main__":
    asyncio.run(main())