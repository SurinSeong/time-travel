import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

KAKAO_URL = os.getenv("KAKAO_URL")

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
os.environ["OPENWEATHERMAP_API_KEY"] = os.getenv("OPENWEATHERMAP_API_KEY")
os.environ["HUGGINGFACE_API_KEY"] = os.getenv("HUGGINGFACE_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

TOOL_DATA_PATH = os.getenv("TOOL_DATA_PATH")

from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
# from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, create_react_agent

# 1. 기능별 도구 함수 정의 (예시는 간단한 형태)
@tool
def get_near_cafe_in_kakao(query: str, lat: float, lon: float) -> list:
    """현재 위치(lat, lon)을 기준으로 사용자에게 카페를 추천합니다."""
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
    """현재 위치(lat, lon)을 기준으로 사용자에게 음식점이나 식당을 추천합니다."""
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
def search_blog(place_name: str) -> list:
    """특정 장소(place_name)에 대한 추가적인 정보인 블로그 후기를 위한 블로그 리스트를 반환합니다."""
    # 블로그 찾기
    url = KAKAO_URL + "/search/blog"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {
        "query": place_name,
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

@tool
async def summarize_blog(model, blog_url: str) -> str:
    """주어진 블로그 URL(blog_url)를 크롤링해서 주요 본문을 추출하고, 3문장으로 요약합니다."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()

        prompt = ChatPromptTemplate.from_messages({
            ("system", "당신은 블로그 요약 전문가입니다. 본문을 바탕으로 3문장으로 내용를 요약해주세요."),
            MessagesPlaceholder("agent_scratchpad"),
            ("human", "크롤링 가능하다면 한국어로 3문장으로 요약하고, 크롤링할 수 없다면 None이라는 값을 반환해주세요.")
        })

        agent = create_react_agent(
            model=model,
            tools=tools,
            prompt=prompt,
            debug=True
        )
        config = RunnableConfig(recursion_limit=10)
        result = await agent.ainvoke({"input": blog_url}, config=config)

    return result["messages"][-1].content

@tool
def find_toilet(model, location: str) -> str:
    """인천 개방 화장실 정보 데이터(df)에서 개방 화장실 위치를 찾습니다."""
    restroom_df = pd.read_csv(TOOL_DATA_PATH + "/restroom_info.csv")
    agent = create_pandas_dataframe_agent(
                                llm=model,
                                df=restroom_df,
                                agent_type="tool-calling",
                                include_df_in_prompt=None,
                                prefix=("당신은 인천의 개방 화장실 데이터를 다루는 어시스턴트입니다. "
                                        f"{location}과 가까운 데이터를 검색하세요. 만약 '인천'이 포함되어 있다면 제거하고 검색하세요."),
                                suffix="한국어로 최대 3곳의 장소를 답변해주세요.",
                                verbose=True,
                                allow_dangerous_code=True)
    result = agent.invoke(location)
    return result.get("output")

@tool
def get_weather(location: str) -> str:
    """현재 위치 또는 특정 위치의 현재 날씨 정보를 반환합니다."""
    tools = load_tools(["openweathermap-api"], llm)
    agent_chain = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    result = agent_chain.invoke(location)
    return result


embedding_model_name = "intfloat/multilingual-e5-large-instruct"

hf_embeddings = HuggingFaceEndpointEmbeddings(
    model=embedding_model_name,
    task="feature-extraction"
)

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH")
VECTOR_DB_NAME = "total_spots_store"

# 저장된 벡터 DB 불러오기
spots_store = Chroma(
                    collection_name=VECTOR_DB_NAME,
                    embedding_function=hf_embeddings,
                    persist_directory=VECTOR_DB_PATH + "/with_hf_embeddings"
                )

@tool
def search_attractions_in_vectorstore(query: str) -> str:
    """벡터DB에서 관광지 정보를 검색해서 반환합니다.."""
    spot_retriever = spots_store.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever=spot_retriever,
        name="vectorstore_search",
        description="Use this tool to search for information in the ChromaDB."
    )
    tools = load_tools([retriever_tool], llm)
    agent_chain = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    result = agent_chain.ainvoke(query)
    return result

# tavilysearch
tavily_search_tool = TavilySearchResults(
                        max_results=10,
                        search_depth="advanced",
                        include_answer=True
                    )
    

TOOLS = [get_near_cafe_in_kakao, get_near_restaurant_in_kakao, search_blog, summarize_blog, find_toilet, get_weather, search_attractions_in_vectorstore, tavily_search_tool]

# 2. LangChain LLM에 도구 바인딩
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)  # LLM이 위 정의된 도구들을 호출 가능:contentReference[oaicite:29]{index=29}

# 3. 노드 함수 정의
def call_llm(state: MessagesState):
    """사용자 메시지에 대해 LLM을 호출합니다. (도구 사용에 대한 결정도 포함합니다.)"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}  # 최신 LLM 응답을 messages에 추가

# ToolNode: LLM이 요청한 tool_call을 실제 실행하는 노드:contentReference[oaicite:30]{index=30}
tool_node = ToolNode(TOOLS)

def analyze_response(state: MessagesState):
    """LLM 최종 답변 추출 (tool_call 없고 content만 있을 때 호출)"""
    final_message = state["messages"][-1]  # AIMessage
    content = getattr(final_message, "content", "")  # 최종 답변 텍스트
    print("Final Answer:", content)
    return {"output": content}  # 필요시 결과를 상태에 저장하거나 반환

# 4. 그래프 구축
builder = StateGraph(MessagesState)
builder.add_node("call_llm", call_llm)
builder.add_node("use_tool", tool_node)
builder.add_node("return_answer", analyze_response)
builder.set_entry_point("call_llm")

# call_llm 실행 후 tool_call 존재 여부에 따라 분기:contentReference[oaicite:31]{index=31}
def need_tool(state: MessagesState):
    last_msg = state["messages"][-1]
    # tool 호출이 있으면 'use_tool'로, 없으면 'return_answer' 노드로 이동
    return "use_tool" if last_msg.tool_calls else "return_answer"

builder.add_conditional_edges("call_llm", need_tool, {"use_tool": "use_tool", "return_answer": "return_answer"})
# 도구 실행 뒤에는 다시 LLM 호출로 루프:contentReference[oaicite:32]{index=32}
builder.add_edge("use_tool", "call_llm")
# 최종 답변 노드 완료 후 그래프 종료
builder.add_edge("return_answer", END)

graph = builder.compile()
