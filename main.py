import streamlit as st
from openai import OpenAI

# 페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="친절한 자산관리 AI", page_icon="💰")
st.title("💰 친절한 자산관리 AI 비서")
st.caption("부동산, 주식, 예·적금 등 고민되는 자산 관리를 쉽고 친절하게 설명해드립니다.")

# 1. API 키 불러오기
# Streamlit Secrets(비밀 금고)에 저장된 'SOLAR_API_KEY'를 안전하게 가지고 옵니다.
try:
    api_key = st.secrets["SOLAR_API_KEY"]
except KeyError:
    st.error("SOLAR_API_KEY가 Streamlit Secrets에 설정되지 않았습니다. Secrets 설정을 확인해주세요.")
    st.stop()

# 2. OpenAI 클라이언트 초기화 (Solar API 서버 연결)
# Upstage의 Solar API 주소와 Secrets에서 가져온 키를 연결합니다.
client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)

# 3. 세션 상태(Session State)에 대화 기록 저장소 만들기
# 앱이 새로고침되어도 이전 대화 내용이 사라지지 않도록 세션 메모리에 저장합니다.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "너는 친절한 자산운용가야. 사용자가 자산 관리 경험이 없는 초년생 정도로 생각하고 전문용어와 함께 쉬운 예시를 사용해서 답해"
        }
    ]

# 4. 화면에 이전 대화 내역 그려주기
# 시스템 프롬프트를 제외한 사용자(user)와 AI(assistant)의 대화만 말풍선으로 보여줍니다.
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. 사용자 메시지 입력 받기
if prompt := st.chat_input("예: '사회초년생인데 월급 200만 원으로 적금이랑 주식 비중을 어떻게 나눠야 할까?'"):
    # 사용자가 입력한 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. AI 답변 생성 및 스트리밍 출력
    with st.chat_message("assistant"):
        message_placeholder = st.empty()  # 글자가 실시간으로 채워질 빈 공간 생성
        full_response = ""

        try:
            # Solar API 호출 (solar-open2 모델 사용, 빠른 응답을 위해 reasoning_effort='none' 설정)
            response = client.chat.completions.create(
                model="solar-open2",
                messages=st.session_state.messages,
                stream=True,  # 실시간 스트리밍 답변 활성화
                extra_body={"reasoning_effort": "none"}  # 추론 기능을 꺼서 답이 빠르게 나오도록 설정
            )

            # 스트리밍되어 들어오는 글자 조각(chunk)들을 하나씩 붙여서 화면에 출력
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")  # 커서 효과 표현
            
            # 답변 완성을 위해 커서(▌)를 빼고 최종 텍스트 출력
            message_placeholder.markdown(full_response)

            # 완성된 AI 답변을 대화 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            # 에러 발생 시 사용자에게 친절한 한국어 안내 메시지 표시
            message_placeholder.markdown("⚠️ 죄송합니다. 답변을 생성하는 중에 잠시 문제가 발생했어요. 잠시 후 다시 시도해 주세요!")
