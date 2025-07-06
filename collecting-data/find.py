import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 검색해서 해당 장소가 있는지 찾기
def find_spot_button(driver, first_address, second_address, info):
    try:
        # iframe 전환
        iframe_element = driver.find_element(By.ID, "searchIframe")
        driver.switch_to.frame(iframe_element)

        # 페이지 로딩 대기 + 항목 찾기
        spots = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li')))
        if spots:
            for spot in spots:
                # 메인 주소 일단 얻어두기
                main_address = WebDriverWait(spot, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.Pb4bU"))).text

                # 첫 번째 확인하기
                if first_address in main_address:
                    # 주소 버튼 열기
                    button = WebDriverWait(spot, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.qbGlu > div.ouxiq > div.d7iiF > div > span:nth-child(2) > a")))
                    button.click()
                    time.sleep(1)

                    # 지번 + 도로명 주소
                    addresses = spot.find_elements(By.CSS_SELECTOR, "span.hAvkz")
                    for address in addresses:
                        if second_address in address.text:
                            break
                        
                    button = spot.find_element(By.CSS_SELECTOR, "div.qbGlu > div.ouxiq > div.ApCpt > a")
                    return button

            else:
                print(f"{info['name']} - 해당 장소가 없습니다.")
                return None
                
        else:
            print(f"{info['name']} - 해당 장소가 없습니다.")
            return None
    
    except Exception as e:
        print("바로 entryIframe을 찾아봅니다. - {e}")
        return "next"


def is_entry_iframe(driver, info):
    try:
        # iframe 전환
        driver.switch_to.default_content()
        iframe_element = driver.find_element(By.ID, "entryIframe")
        driver.switch_to.frame(iframe_element)
        return True
    
    except Exception as e:
        print(f"{info['name']} - 없음 ({e})")
        return False
    
# 이미지 정보 얻기
def find_image(driver, info):
    try:
        main_image = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.fNygA > a > img"))).get_attribute('src')
        if main_image:
            return main_image

    except Exception as e:
        print(f"{info['name']} - 대표 사진 없음")
        return None

# 전화번호 얻기
def find_tel(driver):
    tel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vV_z_ > span.xlx7Q"))).text
    if tel:
        return tel
    else:
        return None

# 홈페이지 얻기
def find_homepage(driver):
    homepage = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vV_z_ > div.jO09N > a"))).get_attribute("href")
    if homepage:
        return homepage
    else:
        return None
    
# overview 얻기
def find_overview(driver):
    sections = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.place_section")))
    for section in sections:
        title = WebDriverWait(section, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h2 > div.place_section_header_title"))).text
        if title == "소개":
            overview = WebDriverWait(section, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.place_section_content > div > div.Ve1Rp > div.T8RFa.CEyr5"))).text
            if overview:
                return overview
    else:
        return None

# 이런 점이 좋았어요 더보기 버튼 누르기
def find_additional_button(driver):
    try:
        button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "dP0sq")))
        print("더보기 버튼 확인")
        button.click()
        time.sleep(2)

    except:
        print("바로 '이런점이 좋았어요'를 가져옵니다.")

# 이런 점이 좋았어요 얻기
def find_good_points(section, good_list, info):
    try:
        good_points = section.find_elements(By.CSS_SELECTOR, "div.place_section_content > div.wvfSn > div.mrSZf > ul > li")
        for good_point in good_points:
            good_point_content = good_point.find_element(By.CSS_SELECTOR, "div.vfTO3 > span.t3JSf").text.strip('"')
            good_point_number = good_point.find_element(By.CSS_SELECTOR, "div.vfTO3 > span.CUoLy").text.split("\n")[1]
            good_list.append(f"{good_point_content}({good_point_number})")
        
        return good_list
    
    except Exception as e:
        print(f"{info['name']} - 이런 점이 좋았어요를 찾을 수 없습니다.")
        return None
