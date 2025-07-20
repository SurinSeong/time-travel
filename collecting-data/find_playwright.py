import asyncio

# 검색해서 해당 장소가 있는지 찾기
async def find_spot_button_playwright(page, first_address, second_address, info):
    try:
        # iframe 전환
        iframe_element = await page.query_selector("#searchIframe")
        if iframe_element:
            frame = await iframe_element.content_frame()
            
            # 페이지 로딩 대기 + 항목 찾기
            await frame.wait_for_selector('#_pcmap_list_scroll_container > ul > li', timeout=30000)
            spots = await frame.query_selector_all('#_pcmap_list_scroll_container > ul > li')
            
            if spots:
                for spot in spots:
                    # 메인 주소 일단 얻어두기
                    main_address_element = await spot.query_selector("span.Pb4bU")
                    if main_address_element:
                        main_address = await main_address_element.text_content()

                        # 첫 번째 확인하기
                        if first_address in main_address:
                            # 주소 버튼 열기
                            button = await spot.query_selector("div.qbGlu > div.ouxiq > div.d7iiF > div > span:nth-child(2) > a")
                            if button:
                                await button.click()
                                await page.wait_for_timeout(1000)

                                # 지번 + 도로명 주소
                                addresses = await spot.query_selector_all("span.hAvkz")
                                for address in addresses:
                                    address_text = await address.text_content()
                                    if second_address in address_text:
                                        break
                                    
                                result_button = await spot.query_selector("div.qbGlu > div.ouxiq > div.ApCpt > a")
                                return result_button
                else:
                    print(f"{info['title']} - 해당 장소가 없습니다.")
                    return None
                    
            else:
                print(f"{info['title']} - 해당 장소가 없습니다.")
                return None
    
    except Exception as e:
        print(f"바로 entryIframe을 찾아봅니다. - {e}")
        return "next"


async def is_entry_iframe_playwright(page, info):
    try:
        # iframe 전환
        iframe_element = await page.query_selector("#entryIframe")
        if iframe_element:
            frame = await iframe_element.content_frame()
            if frame:
                print("iframe 찾음")
                return True
        print("iframe 못찾음.")
        return False
    
    except Exception as e:
        print(f"{info['title']} - 없음 ({e})")
        return False

# 이미지 정보 얻기
async def find_image_playwright(page, info):
    try:
        # 현재 프레임에서 이미지 찾기
        frames = page.frames
        for frame in frames:
            try:
                image_element = await frame.query_selector("div.fNygA > a > img")
                if image_element:
                    main_image = await image_element.get_attribute('src')
                    if main_image:
                        return main_image
            except:
                continue
        return None

    except Exception as e:
        print(f"{info['title']} - 대표 사진 없음")
        return None

# 전화번호 얻기
async def find_tel_playwright(icon):
    try:
        tel_element = await icon.query_selector("div.vV_z_ > span.xlx7Q")
        if tel_element:
            tel = await tel_element.text_content()
            return tel
        return None
    except:
        return None

# 홈페이지 얻기
async def find_homepage_playwright(icon):
    try:
        homepage_element = await icon.query_selector("div.vV_z_ > div.jO09N > a")
        if homepage_element:
            homepage = await homepage_element.get_attribute("href")
            return homepage
        return None
    except:
        return None
    
# overview 얻기
async def find_overview_playwright(page):
    try:
        # 모든 프레임에서 찾기
        frames = page.frames
        for frame in frames:
            try:
                sections = await frame.query_selector_all("div.place_section")
                for section in sections:
                    title_element = await section.query_selector("h2 > div.place_section_header_title")
                    if title_element:
                        title = await title_element.text_content()
                        if title == "소개":
                            overview_element = await section.query_selector("div.place_section_content > div > div.Ve1Rp > div.T8RFa.CEyr5")
                            if overview_element:
                                overview = await overview_element.text_content()
                                if overview:
                                    return overview
            except:
                continue
        return None
    except:
        return None

# 이런 점이 좋았어요 더보기 버튼 누르기
async def find_additional_button_playwright(page):
    try:
        # 모든 프레임에서 찾기
        frames = page.frames
        for frame in frames:
            try:
                button = await frame.query_selector("a.dP0sq")
                if button:
                    print("더보기 버튼 확인")
                    await button.click()
                    await page.wait_for_timeout(2000)
                    return
            except:
                continue
        print("바로 '이런점이 좋았어요'를 가져옵니다.")
    except:
        print("바로 '이런점이 좋았어요'를 가져옵니다.")

# 이런 점이 좋았어요 얻기
async def find_good_points_playwright(section, good_list, info):
    try:
        good_points = await section.query_selector_all("div.place_section_content > div.wvfSn > div.mrSZf > ul > li")
        for good_point in good_points:
            good_point_content_element = await good_point.query_selector("div.vfTO3 > span.t3JSf")
            good_point_number_element = await good_point.query_selector("div.vfTO3 > span.CUoLy")
            
            if good_point_content_element and good_point_number_element:
                good_point_content = await good_point_content_element.text_content()
                good_point_number_text = await good_point_number_element.text_content()
                
                # 따옴표 제거
                good_point_content = good_point_content.strip('"')
                # 줄바꿈으로 분할 후 두 번째 부분 가져오기
                good_point_number = good_point_number_text.split("\n")[1] if "\n" in good_point_number_text else good_point_number_text
                
                good_list.append(f"{good_point_content}({good_point_number})")
        
        return good_list
    
    except Exception as e:
        print(f"{info['name']} - 이런 점이 좋았어요를 찾을 수 없습니다.")
        return None