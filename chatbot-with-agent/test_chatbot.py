#!/usr/bin/env python3
"""
인천 토박이 친구 챗봇 테스트 파일
"""

import os
from dotenv import load_dotenv
from graph_module import make_graph

def main():
    # 환경 변수 로드
    load_dotenv()
    
    # 그래프 생성
    print("챗봇 그래프를 생성하고 있습니다...")
    graph = make_graph()
    
    print("그래프 생성 완료!")
    print("\n=== 인천 토박이 친구 챗봇 ===")
    print("안녕! 나는 인천 토박이 친구야! 뭐든 물어봐~")
    print("종료하려면 'quit' 또는 'exit'를 입력해줘!")
    
    # 대화 시작
    config = {"configurable": {"thread_id": "test_thread"}}
    
    while True:
        try:
            user_input = input("\n너: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("그럼 이만! 또 놀러와~")
                break
            
            if not user_input:
                continue
            
            # 그래프 실행
            result = graph.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            
            # 응답 출력
            if result and "messages" in result:
                for message in result["messages"]:
                    if hasattr(message, 'content') and message.content:
                        print(f"\n챗봇: {message.content}")
            
        except KeyboardInterrupt:
            print("\n\n그럼 이만! 또 놀러와~")
            break
        except Exception as e:
            print(f"\n오류가 발생했어: {e}")
            print("다시 시도해봐!")

if __name__ == "__main__":
    main()
