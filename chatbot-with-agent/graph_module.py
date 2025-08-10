# 필요한 라이브러리 로드
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

from typing import Annotated, TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


from tool_module import *

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# LLM 정의 - 인천 토박이 친구 페르소나 설정
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
)

# 상태 정의
class State(TypedDict):
    # 메시지 정의하기
    messages: Annotated[list, add_messages]
    ask_human: bool
    question_analysis: dict  # 질문 분석 결과
    current_step: str  # 현재 처리 단계

# human 요청 시 사용되는 스키마
class HumanRequest(BaseModel):
    """Forward the conversation to an expert. Use when you can't assist directly or the user needs assistance that exceeds your authority.
    To use this function, pass the user's 'request' so that an expert can provide appropriate guidance."""
    request: str

# 도구 목록
TOOLS = [
    analyze_user_question,
    search_spot_tool_in_db,
    search_tool_in_web,
    open_weather_map,
    restroom_tool,
    get_near_cafe_in_kakao,
    get_near_restaurant_in_kakao,
    search_blog,
    get_detail_info,
    ask_for_clarification,
    parse_gps_coordinates,
    search_restaurants_by_location,
    search_cafes_by_location
]

# llm에 TOOLS 바인딩
llm_with_tools = llm.bind_tools(TOOLS)

# 질문 분석 노드
def analyze_question_node(state: State):
    """사용자의 질문을 분석하여 어떤 종류의 질문인지 분류합니다."""
    last_message = state["messages"][-1]
    
    if isinstance(last_message, HumanMessage):
        # 질문 분석 실행
        analysis_result = analyze_user_question(last_message.content)
        
        return {
            "question_analysis": analysis_result,
            "current_step": "analysis_complete"
        }
    
    return {
        "question_analysis": {},
        "current_step": "no_analysis_needed"
    }

# 챗봇 함수 정의 - 인천 토박이 친구 페르소나 적용
def chatbot(state: State):
    # 시스템 메시지에 페르소나 설정
    system_message = """너는 인천 토박이인 친한 친구야! 반말과 친근감 있는 말투로 대화해줘.
    
    사용자의 질문을 분석해서 적절한 도구를 사용해서 답변해줘:
    1. 인천 관광지 관련 질문이면 벡터DB를 먼저 검색해
    2. 벡터DB에서 답이 안 나오면 웹 검색을 해
    3. 맛집/카페 질문이면 카카오 API로 검색해
    4. 블로그 후기가 필요하면 카카오 블로그 검색 후 크롤링해
    5. 질문이 명확하지 않으면 구체적으로 물어봐
    
    항상 친근하고 반말로 대화해줘!"""
    
    # 시스템 메시지 추가
    messages_with_system = [{"role": "system", "content": system_message}] + state["messages"]
    
    response = llm_with_tools.invoke(messages_with_system)

    # 사람에게 질문할지 여부 초기화
    ask_human = False

    # 도구 호출이 있고, 이름이 'HumanRequest' 인 경우
    if response.tool_calls and response.tool_calls[0]["name"] == HumanRequest.__name__:
        ask_human = True

    # 메시지 호출 및 반환
    return {"messages": [response], "ask_human": ask_human}

# 사람의 개입이 필요할 경우의 노드
# 응답 메시지 생성 함수
def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )

# 인간 노드 처리하기
def human_node(state: State):
    new_messages = []

    if not isinstance(state["messages"][-1], ToolMessage):
        # 사람으로부터 응답이 없는 경우
        new_messages.append(
            create_response("No response from human.", state["messages"][-1])
        )

    return {
        # 새로운 메시지 추가
        "messages": new_messages,
        # 플래그 해제
        "ask_human": False
    }

# 조건부 논리 정의 함수
def select_next_node(state: State):
    # 인간에게 질문 여부 확인
    if state["ask_human"]:
        return "human"
    
    # 질문 분석이 필요한 경우
    if "question_analysis" not in state or not state["question_analysis"]:
        return "analyze"
    
    # 이전과 동일한 경로
    return tools_condition(state)

# 그래프 생성 함수
def make_graph():

    graph_builder = StateGraph(State)
    
    # 도구 노드
    tool_node = ToolNode(tools=TOOLS)

    # 노드 추가하기
    graph_builder.add_node("analyze", analyze_question_node)  # 질문 분석 노드
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("human", human_node)

    # 조건부 엣지 추가
    graph_builder.add_conditional_edges(
        "analyze",
        lambda x: "chatbot",  # 분석 후 항상 챗봇으로
        {"chatbot": "chatbot"}
    )
    
    graph_builder.add_conditional_edges(
        "chatbot",
        select_next_node,
        {"human": "human", "tools": "tools", "analyze": "analyze", END: END}
    )

    # 엣지 추가하기
    graph_builder.add_edge(START, "analyze")  # 시작 시 질문 분석부터
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("human", "chatbot")

    # 대화 내용 기억 tool
    memory = MemorySaver()
    
    # 컴파일
    graph = \
    graph_builder.compile(
        checkpointer=memory,
        interrupt_before=["human"]
    )

    return graph


# if __name__ == "__main__":
#     graph = make_graph()

#     from IPython.display import Image, display
#     from langchain_core.runnables.graph import MermaidDrawMethod

#     display(
#         Image(
#             graph.get_graph().draw_mermaid_png(
#                 draw_method=MermaidDrawMethod.API,
#             )
#         )
#     )