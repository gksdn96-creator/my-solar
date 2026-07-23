import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# 페이지 설정
st.set_page_config(
    page_title="FinAI - 종합 자산관리 플랫폼",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
    .metric-up { color: #e15759; font-weight: bold; }
    .metric-down { color: #4e79a7; font-weight: bold; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("📊 FinAI 종합 자산관리 플랫폼")
st.caption("금융자산(주식, 부동산, 은행) 데이터와 AI 투자 가이드의 통합 연결")

st.divider()

# ==========================================
# 1. 증권 주요 정보 (Market Overview)
# ==========================================
col_sec_title, col_sec_more = st.columns([8, 2])
with col_sec_title:
    st.subheader("📈 주요 증시 및 환율")
with col_sec_more:
    st.page_link("pages/00_증권.py", label="증권 더보기 ↗", use_container_width=True)

# yfinance를 활용한 실시간 데이터 모의 수집 (한국투자증권 API 확장 가능)
@st.cache_data(ttl=300)
def get_main_market_data():
    tickers = {
        "코스피": "^KS11",
        "코스닥": "^KQ11",
        "나스닥": "^IXIC",
        "USD/KRW": "KRW=X"
    }
    data = {}
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                diff = curr - prev
                pct = (diff / prev) * 100
                data[name] = (curr, diff, pct)
            else:
                data[name] = (0, 0, 0)
        except:
            data[name] = (0, 0, 0)
    return data

market_data = get_main_market_data()
cols = st.columns(4)

for idx, (name, (val, diff, pct)) in enumerate(market_data.items()):
    with cols[idx]:
        delta_str = f"{'▲' if diff >= 0 else '▼'} {abs(diff):,.2f} ({pct:+.2f}%)"
        st.metric(label=name, value=f"{val:,.2f}", delta=delta_str, delta_color="normal" if diff >= 0 else "inverse")

st.divider()

# ==========================================
# 2. 부동산 거래량 우수 지역 & 3. 은행 주요 상품
# ==========================================
col_left, col_right = st.columns(2)

with col_left:
    col_re_title, col_re_more = st.columns([7, 3])
    with col_re_title:
        st.subheader("🏠 지난주 거래량 상위 지역 (부동산)")
    with col_re_more:
        st.page_link("pages/01_부동산.py", label="부동산 더보기 ↗", use_container_width=True)
    
    # 국토교통부 실거래가 Open API 확장용 샘플 데이터
    re_data = pd.DataFrame({
        "지역명": ["서울시 강남구", "경기도 성남시 분당구", "서울시 송파구", "경기도 화성시"],
        "주간 거래량": [142, 128, 115, 98],
        "평균 매매가(억)": [24.5, 14.2, 18.9, 6.8],
        "전주 대비": ["▲ 12%", "▲ 8%", "▼ 3%", "▲ 15%"]
    })
    st.dataframe(re_data, hide_index=True, use_container_width=True)

with col_right:
    col_bk_title, col_bk_more = st.columns([7, 3])
    with col_bk_title:
        st.subheader("🏦 추천 예적금 및 IRP 상품")
    with col_bk_more:
        st.page_link("pages/02_은행.py", label="은행 더보기 ↗", use_container_width=True)
    
    # 금융감독원 금융상품통합비교 공시 API 확장용 샘플 데이터
    bank_data = pd.DataFrame({
        "은행명": ["KB국민", "신한은행", "하나은행", "NH농협"],
        "상품 유형": ["정기예금", "적금", "IRP(개인형퇴직연금)", "정기예금"],
        "상품명": ["KB Star 정기예금", "신한 알쏠 적금", "하나 개인형 IRP", "NH올원 파킹예금"],
        "최고 금리": ["3.85%", "4.20%", "3.90%", "3.70%"]
    })
    st.dataframe(bank_data, hide_index=True, use_container_width=True)

st.divider()

# ==========================================
# 4. 하단 AI 투자 가이드 챗봇
# ==========================================
st.subheader("🤖 AI 투자 가이드 챗봇")
st.caption("주식, 부동산 대출, 금융 상품에 대해 자유롭게 질문해보세요.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 자산관리 AI 가이드입니다. 예적금 금리 비교, 주가 전망, 부동산 대출 등 궁금한 점을 물어보세요."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("질문을 입력하세요 (예: 코스피 전망 알려줘, 전세자금대출 금리 비교해줘)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Simple Rule-based AI Response Logic (LLM API 연동 가능)
    response = "죄송합니다. 요청하신 내용에 대한 분석 결과를 생성하는 중입니다."
    if "코스피" in prompt or "주식" in prompt:
        response = "현재 코스피 지수는 주요 이평선 상단에서 등락을 반복하고 있습니다. scikit-learn 예측 모델 기준 상향 모멘텀이 유지되고 있으나 환율 변동성에 유의하세요."
    elif "부동산" in prompt or "대출" in prompt:
        response = "부동산 매매 시 주택담보대출(LTV/DSR) 한도를 우선 확인해야 합니다. 현재 주요 시중은행 주담대 변동금리는 평균 4.1%~4.8% 수준입니다."
    elif "예금" in prompt or "적금" in prompt or "은행" in prompt:
        response = "현재 12개월 기준 주요 시중은행 정기예금 최고 금리는 3.8%~4.2% 수준입니다. '02_은행' 페이지에서 세부 우대금리 조건을 비교해보세요."
    else:
        response = f"'{prompt}'에 대한 포트폴리오 영향도를 분석했습니다. 종합 자산 배분 차원에서 현금 비중 20% 유지를 권장합니다."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
