#!/usr/bin/env python3
"""
LangGraph 흐름을 시각화하는 파일
"""

import os
from dotenv import load_dotenv
from graph_module import make_graph

def visualize_graph():
    """LangGraph의 흐름을 시각화합니다."""
    
    # 환경 변수 로드
    load_dotenv()
    
    # 그래프 생성
    print("그래프를 생성하고 있습니다...")
    graph = make_graph()
    
    print("그래프 생성 완료!")
    print("\n=== LangGraph 흐름도 ===")
    
    # Mermaid 형식으로 그래프 그리기
    try:
        from langchain_core.runnables.graph import MermaidDrawMethod
        
        # Mermaid 다이어그램 생성
        mermaid_code = graph.get_graph().draw_mermaid()
        print("\n📊 Mermaid 다이어그램 코드:")
        print("=" * 50)
        print(mermaid_code)
        print("=" * 50)
        
        # PNG 이미지로 저장 시도
        try:
            png_data = graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            
            # 이미지 파일로 저장
            with open("graph_flow.png", "wb") as f:
                f.write(png_data)
            print("\n✅ 그래프 이미지가 'graph_flow.png'로 저장되었습니다!")
            
        except Exception as e:
            print(f"\n⚠️ PNG 이미지 생성 실패: {e}")
            print("Mermaid 코드를 온라인 에디터에서 확인해보세요!")
            
    except ImportError:
        print("Mermaid 시각화를 위한 라이브러리가 설치되지 않았습니다.")
        print("pip install langchain-core를 실행해주세요.")
        
        # 대안: 텍스트로 그래프 구조 설명
        print("\n📋 그래프 구조 설명:")
        print_graph_structure()

def print_graph_structure():
    """텍스트로 그래프 구조를 설명합니다."""
    print("""
    🔄 LangGraph 워크플로우 흐름:
    
    START
      ↓
    [analyze] → 질문 분석 노드
      ↓
    [chatbot] → 챗봇 처리 노드
      ↓
    ┌─────────────────────────────────────┐
    │           조건부 분기               │
    └─────────────────────────────────────┘
      ↓
    ┌─────────┬─────────┬─────────┬──────┐
    │  human  │  tools  │ analyze │ END  │
    │   ↓     │   ↓     │   ↓     │      │
    │ 인간노드 │ 도구노드 │ 분석노드 │ 종료  │
    │   ↓     │   ↓     │   ↓     │      │
    └─────────┴─────────┴─────────┴──────┘
      ↓         ↓         ↓
    [chatbot] [chatbot] [chatbot]
      ↓         ↓         ↓
      └─────────┴─────────┘
              ↓
            END
    
    📝 노드 설명:
    
    1. analyze (질문 분석):
       - 사용자 질문을 분석하여 유형 분류
       - 관광지, 맛집, 카페, 날씨 등으로 분류
       - 위치 정보 추출
    
    2. chatbot (챗봇 처리):
       - 질문 분석 결과를 바탕으로 적절한 도구 선택
       - 인천 토박이 친구 페르소나로 응답
       - 다음 단계 결정
    
    3. tools (도구 실행):
       - 벡터DB 검색, 카카오 API, 웹 검색 등
       - 실제 정보 검색 및 처리
    
    4. human (인간 개입):
       - 질문이 명확하지 않을 때 사용자에게 추가 질문
       - 명확화가 필요한 경우 처리
    
    🔧 주요 도구들:
    
    • analyze_user_question: 질문 분석 및 분류
    • search_spot_tool_in_db: 벡터DB 관광지 검색
    • search_tool_in_web: Tavily 웹 검색
    • get_near_restaurant_in_kakao: 카카오 맛집 검색
    • get_near_cafe_in_kakao: 카카오 카페 검색
    • search_blog: 카카오 블로그 검색
    • get_detail_info: 블로그 내용 크롤링
    • ask_for_clarification: 질문 명확화 요청
    
    💬 대화 흐름:
    
    사용자 질문 → 질문 분석 → 챗봇 처리 → 도구 선택 → 
    정보 검색 → 응답 생성 → 다음 단계 결정 → 반복 또는 종료
    """)

if __name__ == "__main__":
    visualize_graph()
