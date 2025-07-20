import os
from dotenv import load_dotenv
load_dotenv()

from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_upstage import ChatUpstage
from langchain.tools.retriever import create_retriever_tool
import streamlit as st
import time

AGENT_DATA_PATH = os.getenv("AGENT_DATA_PATH")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

## RAG 기반
loader = PyPDFLoader(
            AGENT_DATA_PATH + "/Solar LLM.pdf"
        )

pages = loader.load_and_split()

vectorstore = Chroma.from_documents(pages, UpstageEmbeddings(model="solar-embedding-1-large"))

retriever = vectorstore.as_retriever(k=2)

from langchain_upstage import ChatUpstage

chat = ChatUpstage(upstage_api_key=os.getenv("UPSTAGE_API_KEY"))

# Agent가 스스로 액션을 취하도록 하게 검색 tool을 설정함.
# retriever를 tool로 활용할 수 있도록 함.
retriever_tool = create_retriever_tool(
    retriever,
    "solar_search",    # tool의 이름
    "Searches any questions related to Solar. Always use this tool when user query is related to Solar!",    # tool의 설명 (어느 상황에서 사용해야 할지 정확하게 작성)
)

## 2번째 tool - tavily 검색 엔진 사용하기
tavily_tool = TavilySearchResults()

## 3. 여러 검색엔진을 tool로 사용하기
from langchain_community.utilities import SerpAPIWrapper

params = {
    "engine": "naver",
    "query": "paris",
    "hl": "ko",
}
search = SerpAPIWrapper(params=params, serpapi_api_key=SERPAPI_API_KEY)

from langchain_core.tools import Tool

# agent가 사용할 수 있는 tool로 변경
naver_tool = Tool(
    name="naver_search",
    description="Use Naver search engine",
    func=search.run,
)

tools = [tavily_tool, retriever_tool, naver_tool]

# Agent 생성
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub

prompt = hub.pull("hwchase17/openai-functions-agent")

agent = create_tool_calling_agent(chat, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# result = agent_executor.invoke({"input": "introduce solar llm"})
# print(result)

# 웹사이트 제목
st.title("Chatbot with Tools")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용을 기록하기 위해 셋업
# Streamlit 특성상 활성화하지 않으면 내용이 다 날아감.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# 프롬프트 비용이 너무 많이 소요되는 것을 방지하기 위해
MAX_MESSAGES_BEFORE_DELETION = 4

# 웹사이트에서 유저의 인풋을 받고 위에서 만든 AI 에이전트 실행시켜서 답변 받기
if prompt := st.chat_input("Ask a question!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
# 유저가 보낸 질문이면 유저 아이콘과 질문 보여주기
     # 만약 현재 저장된 대화 내용 기록이 4개보다 많으면 자르기
    if len(st.session_state.messages) >= MAX_MESSAGES_BEFORE_DELETION:
        # Remove the first two messages
        del st.session_state.messages[0]
        del st.session_state.messages[0]  

    with st.chat_message("user"):
        st.markdown(prompt)

# AI가 보낸 답변이면 AI 아이콘이랑 LLM 실행시켜서 답변 받고 스트리밍해서 보여주기
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = agent_executor.invoke({"input": prompt, "chat_history": st.session_state.messages})

        for chunk in result["output"].split(" "):
            full_response += chunk + " "
            time.sleep(0.2)
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})

print("_______________________")
print(st.session_state.messages)