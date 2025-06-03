# backend/langchain_chain.py
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

# 자연어 → 트리 명령 프롬프트 템플릿
prompt = ChatPromptTemplate.from_template("""
너는 홍익대학교의 카테고리 트리를 관리하는 AI야.

학생이 보낸 문장을 읽고, 트리에 추가할 가치가 있는 정보가 있는 경우에만 아래의 JSON 형식으로 응답해.

- 반드시 JSON만 출력해.
- 무의미한 대화(예: 인사, 잡담, 감탄사, 감정 표현 등)는 {{"path": null, "value": null}}을 반환해야 해.
- 루트는 무조건 "홍익대학교"로 시작하는 path 배열로 출력해.
- 정보가 부족하거나 불확실하면 {{"path": null, "value": null}}을 반환해야 해.
- 학생이 보낸 문장이 카테고리만 추가하려는 의도이면 value값으로 null을 넣어줘.
- 만약 학생이 보낸 문장이 카테고리에 정보를 추가하려는 의도가 보이면 value값으로 그 정보를 추가해줘.
                                          
예시:
입력: "홍익대학교에 향차이라는 중국 음식점이 있어"
출력: {{ "path": ["홍익대학교", "근처 음식점", "중식", "향차이"], "value": null }}

입력: "홍익대학교에 향차이라는 중국 음식점이 있는데 짜장면이 1000원이야"
출력: {{ "path": ["홍익대학교", "근처 음식점", "중식", "향차이"], "value": "짜장면 : 1000원" }}

입력: "오늘 시험 잘 봐야지"
출력: {{ "path": null, "value": null }}

입력: "ㅎㅇ"
출력: {{ "path": null, "value": null }}

문장: {user_input}
""")

# LLMChain 생성
chain = LLMChain(llm=llm, prompt=prompt)

# 외부에서 호출되는 함수
def extract_tree_command(user_input: str) -> str:
    return chain.run({"user_input": user_input})
