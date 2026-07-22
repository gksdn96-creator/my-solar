📁 Asset_Management_App/
│── .streamlit/
│   └── secrets.toml        # SOLAR_API_KEY 저장
│── main.py                 # Streamlit 실행 메인 파일
│── requirements.txt        # openai, pandas 등
└── data/                   # 사용자 자산 데이터 및 상품 캐시 데이터
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# -------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Solar AI 종합 자산 관리 대시보드",
    page_icon="💰",
    layout="wide"
)

# 앱 제목 및 소개
st.title("💰 Solar AI 자산 진단 & 상담 대시보드")
st.caption("내 보유 자산과 소득 정보를 입력하고, Solar AI 비서에게 맞춤형 포트폴리오 진단을 받아보세요.")

# -------------------------------------------------------------------
# 2. Solar API 클라이언트 초기화 (Secrets 안전 불러오기)
# -------------------------------------------------------------------
try:
    api_key = st.secrets["SOLAR_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("⚠️ Secrets에서 'SOLAR_API_KEY'를 찾을 수 없습니다. `.streamlit/secrets.toml` 파일 또는 Streamlit Cloud Secrets 설정을 확인해주세요.")
    st.stop()

# Upstage Solar API 설정 (OpenAI 라이브러리 사용)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)

# -------------------------------------------------------------------
# 3. 사이드바: 사용자 프로필 및 보유 자산 입력
# -------------------------------------------------------------------
with st.sidebar:
    st.header("👤 사용자 프로필")
    user_age = st.number_input("나이 (세)", min_value=18, max_value=100, value=28, step=1)
    monthly_income = st.number_input("월 순소득 (만원)", min_value=0, value=250, step=10)
    risk_tolerance = st.selectbox(
        "투자 성향",
        ["안정형 (원금 보존 선호)", "위험중립형 (적정한 수익 및 위험)", "공격투자형 (고수익 추구)"]
    )

    st.markdown("---")
    st.header("📊 보유 자산 등록 (단위: 만원)")
    
    cash = st.number_input("💵 예금 / 적금 / 현금성", min_value=0, value=1000, step=50)
    stock = st.number_input("📈 주식 / ETF / 채권", min_value=0, value=500, step=50)
    real_estate = st.number_input("🏠 부동산 (전세보증금 포함)", min_value=0, value=0, step=500)
    crypto_other = st.number_input("🪙 가상자산 / 기타", min_value=0, value=0, step=10)

    # 총 자산 계산
    total_assets = cash + stock + real_estate + crypto_other

    st.markdown("---")
    st.metric(label="총 보유 자산", value=f"{total_assets:,} 만원")

# -------------------------------------------------------------------
# 4. 메인 화면: 자산 현황 시각화 & 지표 대시보드
# -------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 자산 배분 비중")
    if total_assets > 0:
        asset_data = pd.DataFrame({
            "자산군": ["예적금/현금", "주식/채권", "부동산", "기타/가상자산"],
            "금액": [cash, stock, real_estate, crypto_other]
        })
        # 도넛 차트 생성
        fig = px.pie(
            asset_data,
            values="금액",
            names="자산군",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("사이드바에서 자산 금액을 입력해주세요.")

with col2:
    st.subheader("🔍 주요 자산 지표 분석")
    
    # 지표 계산
    cash_ratio = (cash / total_assets * 100) if total_assets > 0 else 0
    stock_ratio = (stock / total_assets * 100) if total_assets > 0 else 0
    re_ratio = (real_estate / total_assets * 100) if total_assets > 0 else 0

    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("현금성 자산 비중", f"{cash_ratio:.1f}%")
        st.metric("부동산 집중도", f"{re_ratio:.1f}%")
    with metric_col2:
        st.metric("투자 자산 비중", f"{stock_ratio:.1f}%")
        emergency_months = (cash / (monthly_income * 0.5)) if monthly_income > 0 else 0
        st.metric("비상금 여력", f"약 {emergency_months:.1f}개월분")

    st.caption("💡 Tip: 사회초년생의 경우 3~6개월 치 생활비 수준의 현금성 자산을 보유하는 것이 권장됩니다.")

st.markdown("---")

# -------------------------------------------------------------------
# 5. AI 프롬프트 생성 및 대화 세션 관리
# -------------------------------------------------------------------
# 사용자의 현재 프로필 및 자산 상태를 기반으로 동적 시스템 프롬프트 작성
system_prompt_content = f"""
너는 친절하고 실력 있는 전문 자산운용가야.
사용자가 자산 관리 경험이 부족한 사회초년생이나 금융 초보자라고 생각하고,
쉬운 예시와 비유, 그리고 명확한 전문용어를 함께 곁들여서 알기 쉽게 상담해줘.

[현재 상담 사용자의 자산 및 프로필 정보]
- 나이: {user_age}세
- 월 순소득: {monthly_income:,}만 원
- 투자 성향: {risk_tolerance}
- 총 자산: {total_assets:,}만 원
  * 예적금/현금: {cash:,}만 원 ({cash_ratio:.1f}%)
  * 주식/채권: {stock:,}만 원 ({stock_ratio:.1f}%)
  * 부동산: {real_estate:,}만 원 ({re_ratio:.1f}%)
  * 가상자산/기타: {crypto_other:,}만 원

답변 시 사용자의 나이, 소득, 자산 비중을 바탕으로 현실적인 조언(예적금 비중 조절, 적립식 주식 투자, 비상금 마련 등)을 구체적인 예시와 함께 친절하게 제시해줘.
"""

# 세션 내 대화 저장소 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt_content}
    ]
else:
    # 프로필이나 자산 금액이 바뀔 경우 시스템 프롬프트 업데이트
    st.session_state.messages[0] = {"role": "system", "content": system_prompt_content}

# -------------------------------------------------------------------
# 6. AI 채팅 인터페이스
# -------------------------------------------------------------------
st.subheader("💬 Solar AI 자산 관리자와 실시간 상담")

# 빠른 AI 종합 진단 버튼
if st.button("🪄 내 포트폴리오 원클릭 AI 정밀 진단 받기"):
    auto_prompt = "내 현재 나이, 소득, 자산 비중을 바탕으로 제 포트폴리오의 장단점과 앞으로의 자산 운용 전략 3가지를 진단해줘!"
    st.session_state.messages.append({"role": "user", "content": auto_prompt})

# 대화 기록 출력 (시스템 메시지 제외)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 신규 질문 입력 처리
if prompt := st.chat_input("자산 관리에 대해 궁금한 점을 물어보세요 (예: '제 나이에 주식 비중을 더 늘려도 될까요?')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# AI 답변 생성 (마지막 메시지가 사용자인 경우 실행)
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Solar API 호출
            # model은 'solar-open2' 그대로 사용
            # 빠른 답변 생성을 위해 reasoning_effort='none' 전달
            response = client.chat.completions.create(
                model="solar-open2",
                messages=st.session_state.messages,
                stream=True,
                extra_body={"reasoning_effort": "none"}
            )

            # 스트리밍 텍스트 처리
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.markdown("⚠️ 죄송합니다. API 연결 중 오류가 발생했습니다. 키 설정과 네트워크 상태를 확인 후 다시 시도해주세요.")
