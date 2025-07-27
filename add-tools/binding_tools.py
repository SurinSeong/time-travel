import os
from dotenv import load_dotenv

load_dotenv()

KAKAO_URL = os.getenv("KAKAO_URL")

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

import requests
from playwright.async_api import async_playwright
from langchain.agents import tool
from langchain_core.runnables import RunnableConfig
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools import TavilySearchResults
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langgraph.prebuilt import create_react_agent

# 도구 정의
# 1. 근처 맛집, 카페에 대한 정보 알려주기 - 카카로 로컬 API 사용하기
# ex) 근처 맛집 알려줘. -> 이러이러한 곳이 있다 정도만 보여주기 or 관련 블로그 후기까지 보여주기
@tool
def get_near_cafe_in_kakao(query: str, lat: float, lon: float) -> list:
    """Finds cafes near the user's current location using location-based search."""
    # KAKAO local 사용
    url = KAKAO_URL + "/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {
        "query": query,
        "category_group_code": "CE7",
        "x": f"{lon}",
        "y": f"{lat}",
        "size": "10",
        "radius": "1000",
    }

    response = requests.get(url=url, headers=headers, params=params)

    spots = []

    # 요청 성공 확인
    if response.status_code == 200:
        response = response.json()
        spots_info = response["documents"]
        for spot_info in spots_info:
            name = spot_info["place_name"]
            spot_url = spot_info["place_url"]
            address = spot_info["road_address_name"]
            phone = spot_info["phone"]
            latitude = spot_info["y"]
            longtitude = spot_info["x"]
            info = {
                "name": name,
                "address": address,
                "latitude": latitude,
                "longtitude": longtitude,
                "place_url": spot_url,
                "phone_number": phone
            }
            spots.append(info)
    else:
        print(f"HTTP 요청 실패. 응답 코드: {response.status_code}")
    
    return spots


@tool
def get_near_restaurant_in_kakao(query: str, lat: float, lon: float) -> list:
    """Finds popular restaurants near the user's current location using local recommendation data."""
    # KAKAO local 사용
    url = KAKAO_URL + "/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {
        "query": query,
        "category_group_code": "CE7",
        "x": f"{lon}",
        "y": f"{lat}",
        "size": "10",
        "radius": "1000",
    }

    response = requests.get(url=url, headers=headers, params=params)

    spots = []

    # 요청 성공 확인
    if response.status_code == 200:
        response = response.json()
        spots_info = response["documents"]
        for spot_info in spots_info:
            name = spot_info["place_name"]
            spot_url = spot_info["place_url"]
            address = spot_info["road_address_name"]
            phone = spot_info["phone"]
            latitude = spot_info["y"]
            longtitude = spot_info["x"]
            info = {
                "name": name,
                "address": address,
                "latitude": latitude,
                "longtitude": longtitude,
                "place_url": spot_url,
                "phone_number": phone
            }
            spots.append(info)
    else:
        print(f"HTTP 요청 실패. 응답 코드: {response.status_code}")
    
    return spots


# 추가) 블로그 검색
@tool
def search_blog(query: str) -> list:
    """Searches Blog for user-generated reviews and experiences about the specified place."""
    url = KAKAO_URL + "/search/blog"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {
        "query": query,
        "size": "10"
    }
    response = requests.get(url=url, headers=headers, params=params)
    
    blog_list = []

    if response.status_code == 200:
        response = response.json()
        for document in response["documents"]:
            title = document.get("title")
            contents = document.get("contents")
            blog_name = document.get("blogname")
            blog_url = document.get("url")
            info = {
                "title": title,
                "contents": contents,
                "blog_name": blog_name,
                "blog_url": blog_url,
            }
            blog_list.append(info)
    
    else:
        print(f"HTTP 요청 실패. 응답 코드: {response.status_code}")
    
    return blog_list

# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# 크롤링을 위한 툴 불러와야 하는지 - PlayWright Browser Toolkit
async def get_blog_content(model, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()
        
        # prompt = ChatPromptTemplate.from_messages([
        #     ("system", "You are the greatest researcher and summarizer: Summarize and stop when main content found."),
        #     MessagesPlaceholder("agent_scratchpad"),
        #     ("user", "Please visit {url}, extract main content or text under div.se-main-container, summarize in 3 sentences in Korean. If you cannot find blog's content in recursion limit, return ''.")
        # ])
        agent = create_react_agent(model=model,
                                         tools=tools,
                                        #  prompt=prompt,
                                         debug=True)
        
        config = RunnableConfig(recursion_limit=10, callbacks=print_callback)
        result = await agent.ainvoke(
            {
                "messages": [
                    ("system", "You are the greatest researcher and summarizer: Summarize and stop when main content found."),
                    ("user", f"Please visit {url}, extract main content or text under div.se-main-container, summarize in 3 sentences in Korean. If you cannot find blog's content in recursion limit, return ''.")
                ],
            },
            # input=url,
            config=config,

        )
        return result


# 2. 근처 공공시설 알려주기 - 공공데이터포털에서 찾은 API
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

TOOL_DATA_PATH = os.getenv("TOOL_DATA_PATH")

def get_restroom_info(query, model):
    restroom_df = pd.read_csv(TOOL_DATA_PATH + "/restroom_info.csv")
    agent = create_pandas_dataframe_agent(
                                llm=model,
                                df=restroom_df,
                                agent_type="tool-calling",
                                include_df_in_prompt=None,
                                prefix=\
                                    f"""
                                    You are an assistant who organizes open restroom data.
                                    Please answer with the CSV data, {restroom_df}, provided in mind in Korean.
                                    If you find with address, remove '인천' and find the restroom info.
                                    """,
                                suffix="At the end, please provide a concise summary of up to three locations in Korean.",
                                verbose=True,
                                allow_dangerous_code=True)
    result = agent.ainvoke(query)
    
    return result


# 3. 나오지 않는 관광지에 대한 웹 검색하기 - tavily
def get_spots_info_not_in_db(query):
    search = TavilySearchResults(
        max_results=10,
        search_depth="advanced",
    )
    result = search.invoke(query)
    return result

# 4. 벡터 DB에 접근하기
from langchain.tools.retriever import create_retriever_tool

def get_vectorstore_info(query, llm):
    retriever_tool = create_retriever_tool(
        name="vectorstore_search",
        description="Use this tool to search for information in the ChromaDB."
    )
    tools = load_tools([retriever_tool], llm)
    agent_chain = initialize_agent(
        tools=tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    result = agent_chain.ainvoke(query)
    return result


# 5. 대화 내용 기억하는 agent
# 5. 뭔가 일정 관리 같은거를 해주면 좋을텐데

# 날씨 - OpenWeatherMap
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain.agents import AgentType, initialize_agent, load_tools

os.environ["OPENWEATHERMAP_API_KEY"] = os.getenv("OPENWEATHERMAP_API_KEY")

weather = OpenWeatherMapAPIWrapper()

def get_weather_info(llm, query):
    tools = load_tools(["openweathermap-api"], llm)
    agent_chain = initialize_agent(
        tools=tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    result = agent_chain.ainvoke(query)
    return result


# 콜백 함수 정의
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

print_callback = CallbackManager([StreamingStdOutCallbackHandler()])


# 모델 정의
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

import asyncio

async def main():

    query = input("어떤 것이 궁금하세요?\n")
    
    # 특정 장소에 대한 후기
    # blog_list = search_blog(query)
    # if blog_list:
    #     for i, blog in enumerate(blog_list):
    #         print(f"[{i+1}] {blog['blog_url']}")
    #         if blog["blog_url"]:
    #             result = await get_blog_content(model=llm, url=blog["blog_url"])
    #             print(result["messages"][-1].content)

    # # 공공시설 - 화장실 관련
    # result = await get_restroom_info(query, llm)
    # print(result["output"])

    # 오늘 날씨
    result = await get_weather_info(llm, query)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
