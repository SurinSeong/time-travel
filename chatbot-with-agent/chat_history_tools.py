# 메시지 삭제

from langchain_core.messages import RemoveMessage, HumanMessage

# 메시지 개수가 n개 초과 시 오래된 메시지 삭제 및 최신 메시지만 유지
def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 10:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:-3]]}


# 대화 내용 요약 및 메시지 정리 로직
def summarize_messages(state, model):
    # 이전 요약 정보 확인
    summary = state.get("summary", "")

    # 이전 요약 정보가 있다면 요약 메시지 생성
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above in Korean:"
        )
    
    else:
        # 요약 메시지 생성
        summary_message = "Create a summary of the conversation above in Korean:"

    # 요약 메시지와 이전 메시지 결합
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    # 모델 호출
    response = model.invoke(messages)
    # 오래된 메시지 삭제
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-3]]
    # 요약 정보 반환
    return {"summary": response.content, "messages": delete_messages}

