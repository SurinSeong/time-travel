# Time Travel - 인천 토박이 친구 챗봇

인천 지역 정보를 제공하는 AI 챗봇입니다. 인천 토박이 친구처럼 친근하고 반말로 대화하며, 관광지, 맛집, 카페 등 다양한 정보를 제공합니다.

## 🚀 주요 기능

### 1. 질문 분석 및 분류
- 사용자의 질문을 자동으로 분석하여 적절한 도구 선택
- 관광지, 맛집, 카페, 날씨, 화장실 등 질문 유형 자동 분류
- 위치 정보 자동 추출 (예: "인천역 근처", "송도 근처")

### 2. 인천 관광지 정보
- 벡터 데이터베이스를 통한 빠른 관광지 검색
- 벡터DB에서 답이 없을 경우 웹 검색으로 보완

### 3. 맛집 및 카페 추천
- 카카오 API를 통한 지역별 맛집/카페 검색
- 위치 기반 근처 맛집/카페 추천
- 상세 정보 및 연락처 제공

### 4. 블로그 후기 및 리뷰
- 카카오 블로그 검색을 통한 장소별 후기 수집
- 블로그 내용 크롤링 및 요약
- 실제 방문자들의 생생한 후기 제공

### 5. 기타 서비스
- 날씨 정보 제공
- 공공화장실 위치 검색
- 질문이 명확하지 않을 때 구체적 질문 요청

## 🛠️ 기술 스택

- **LangGraph**: 대화 워크플로우 관리
- **LangChain**: AI 도구 및 체인 구성
- **OpenAI GPT-4**: 자연어 처리
- **Chroma/FAISS**: 벡터 데이터베이스
- **Kakao API**: 지역 정보 검색
- **Tavily**: 웹 검색
- **BeautifulSoup**: 웹 크롤링

## 📁 프로젝트 구조

```
chatbot-with-agent/
├── graph_module.py          # LangGraph 워크플로우 정의
├── tool_module.py           # 다양한 도구들 구현
├── test_chatbot.py          # 챗봇 테스트 실행 파일
└── data/                    # 데이터 파일들
```

## 🚀 설치 및 실행

### 1. 환경 변수 설정
`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
TAVILY_API_KEY=your_tavily_api_key
KAKAO_REST_API_KEY=your_kakao_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
KAKAO_URL=https://dapi.kakao.com
DB_PATH=path_to_your_vector_database
RESTROOM_CSV=path_to_restroom_csv_file
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 챗봇 실행
```bash
cd chatbot-with-agent
python test_chatbot.py
```

## 💬 사용 예시

### 관광지 관련
```
너: 인천에 볼만한 곳 어디 있어?
챗봇: 인천에 정말 좋은 곳들이 많아! 벡터DB에서 찾아볼게~
```

### 맛집 관련
```
너: 인천역 근처 맛집 추천해줘
챗봇: 인천역 근처 맛집 찾아볼게! 카카오 API로 검색해보자~
```

### 카페 관련
```
너: 송도에 좋은 카페 있어?
챗봇: 송도 카페 찾아볼게! 근처에 어떤 카페들이 있는지 확인해보자~
```

### 블로그 후기
```
너: 송도 더본 카페 후기 알려줘
챗봇: 송도 더본 카페 후기 찾아볼게! 블로그 검색해서 실제 방문자들의 후기를 가져올게~
```

## 🔧 커스터마이징

### 새로운 도구 추가
`tool_module.py`에 새로운 `@tool` 데코레이터를 사용하여 도구를 추가할 수 있습니다.

### 워크플로우 수정
`graph_module.py`에서 노드와 엣지를 수정하여 워크플로우를 변경할 수 있습니다.

### 페르소나 변경
`chatbot` 함수의 `system_message`를 수정하여 챗봇의 성격을 바꿀 수 있습니다.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
