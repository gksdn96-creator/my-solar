import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 스타일링
# ==========================================
st.set_page_config(
    page_title="All-in-One AI 자산관리 비서",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS로 UI 다듬기
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .chat-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Mock 데이터 생성 함수 (실제 운영 시 API 연동)
# ==========================================
@st.cache_data
def load_market_index():
    return {
        "코스피": {"val": "2,755.30", "delta": "+12.40 (+0.45%)"},
        "코스닥": {"val": "890.15", "delta": "-3.20 (-0.36%)"},
        "나스닥": {"val": "16,388.24", "delta": "+115.80 (+0.71%)"},
        "USD/KRW": {"val": "1,345.50", "delta": "+4.50 (+0.34%)"}
    }

@st.cache_data
def load_real_estate_summary():
    data = {
        "지역": ["서울 강남구", "경기 성남시 분당구", "서울 마포구", "인천 연수구", "대구 수성구"],
        "7일간 거래량": [342, 289, 215, 198, 176],
        "평균 매매가(33평 기준)": ["24.5억", "14.2억", "12.8억", "7.1억", "8.5억"],
        "전주 대비 변동": ["+0.8%", "+0.5%", "+0.2%", "-0.1%", "+0.0%"]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_bank_products_summary():
    data = {
        "기관/은행": ["KB국민은행", "신한은행", "하나은행", "NH농협", "삼성증권"],
        "상품 유형": ["정기예금", "적금", "IRP (개인형퇴직연금)", "정기예금", "IRP 원리금보장"],
        "상품명": ["KB Star 정기예금", "신한 알쏠 적금", "하나 IRP 자산관리", "NH 올원예금", "삼성 IRP"],
        "기본/최고금리": ["3.55% / 3.65%", "3.70% / 4.30%", "3.40% / 3.80%", "3.50% / 3.60%", "3.65% / 3.90%"]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_stock_details():
    stocks = [
        {"종목명": "삼성전자", "코드": "005930", "현재가": 78,500, "등락률": "+1.2%", "PER": 14.2, "추천도": "매수"},
        {"종목명": "SK하이닉스", "코드": "000660", "현재가": 178,000, "등락률": "+2.8%", "PER": 21.5, "추천도": "강력매수"},
        {"종목명": "NAVER", "코드": "035420", "현재가": 189,500, "등락률": "-0.8%", "PER": 28.1, "추천도": "보유"},
        {"종목명": "엔비디아 (NVDA)", "코드": "NVDA", "현재가": "$892.10", "등락률": "+3.4%", "PER": 65.2, "추천도": "매수"},
        {"종목명": "애플 (AAPL)", "코드": "AAPL", "현재가": "$172.50", "등락률": "-0.2%", "PER": 26.8, "추천도": "보유"}
    ]
    return pd.DataFrame(stocks)

@st.cache_data
def load_news():
    return {
        "증권/주식": [
            " [증시] 반도체주 강세로 코스피 상승 마감... 외국인 순매수 지속",
            " 미 연준 금리 인하 시기 논쟁 지속... 나스닥 혼조세"
        ],
        "부동산": [
            " [부동산] 서울 주요 권역 거래량 회복세... 강남/마포 중심으로 신고가 renewal",
            " 수도권 3기 신도시 청약 일정 발표... 실수요자 관심 집중"
        ],
        "금융/은행": [
            " [금융] 시중은행 예적금 금리 소폭 하락... IRP 절세 혜택 상품 인기",
            " 기준금리 동결 기조 속 고금리 파킹통장 경쟁 재열풍"
        ]
    }

# ==========================================
# 3. 사이드바 (상세 정보 및 경제 뉴스)
# ==========================================
with st.sidebar:
    st.title("🔍 세부 자산 & 뉴스")
    st.markdown("---")
    
    sidebar_tab = st.radio("메뉴 선택", ["상세 시장 정보", "카테고리별 경제 뉴스"])
    
    if sidebar_tab == "상세 시장 정보":
        asset_category = st.selectbox("자산 영역 선택", ["주식 종목 상세", "부동산 세부 실거래", "은행/IRP 금리 비교"])
        
        if asset_category == "주식 종목 상세":
            st.subheader("📊 주요 주식 종목")
            st.dataframe(load_stock_details(), use_container_width=True)
            
        elif asset_category == "부동산 세부 실거래":
            st.subheader("🏢 전국 주요 단지 거래가")
            re_df = load_real_estate_summary()
            st.dataframe(re_df, use_container_width=True)
            
        elif asset_category == "은행/IRP 금리 비교":
            st.subheader("🏦 금융상품 금리 비교")
            st.dataframe(load_bank_products_summary(), use_container_width=True)
            
    elif sidebar_tab == "카테고리별 경제 뉴스":
        st.subheader("📰 실시간 경제 뉴스")
        news = load_news()
        news_cat = st.selectbox("뉴스 분야", ["증권/주식", "부동산", "금융/은행"])
        
        for item in news[news_cat]:
            st.info(item)

# ==========================================
# 4. 메인 화면 - 헤더 & 주요 지표 (Metrics)
# ==========================================
st.title("🌐 AI 통합 자산관리 & 투자 가이드 대시보드")
st.caption("주식, 부동산, 예적금 및 IRP 정보를 실시간으로 통합 분석하여 최적의 투자 방향을 제시합니다.")

st.markdown("### 📈 주요 시장 지표 & 환율")
idx_data = load_market_index()
m1, m2, m3, m4 = st.columns(4)

m1.metric("코스피 (KOSPI)", idx_data["코스피"]["val"], idx_data["코스피"]["delta"])
m2.metric("코스닥 (KOSDAQ)", idx_data["코스닥"]["val"], idx_data["코스닥"]["delta"])
m3.metric("나스닥 (NASDAQ)", idx_data["나스닥"]["val"], idx_data["나스닥"]["delta"])
m4.metric("원/달러 환율", idx_data["USD/KRW"]["val"], idx_data["USD/KRW"]["delta"])

st.markdown("---")

# ==========================================
# 5. 메인 화면 - 부동산 & 금융상품 현황
# ==========================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📍 지난주 거래량 상위 부동산 지역")
    re_summary = load_real_estate_summary()
    
    # 그래프 시각화
    fig_re = px.bar(
        re_summary, 
        x="지역", 
        y="7일간 거래량", 
        color="7일간 거래량",
        color_continuous_scale="Viridis",
        title="지역별 거래량 추이"
    )
    fig_re.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_re, use_container_width=True)
    st.dataframe(re_summary[["지역", "평균 매매가(33평 기준)", "전주 대비 변동"]], use_container_width=True)

with col_right:
    st.subheader("🏦 주요 은행 예적금 및 IRP 기준금리")
    bank_summary = load_bank_products_summary()
    
    # 탭을 활용한 카테고리 분리
    tab_dep, tab_irp = st.tabs(["예적금", "IRP/연금"])
    
    with tab_dep:
        st.table(bank_summary[bank_summary["상품 유형"].isin(["정기예금", "적금"])][["기관/은행", "상품명", "기본/최고금리"]])
    
    with tab_irp:
        st.table(bank_summary[bank_summary["상품 유형"].str.contains("IRP")][["기관/은행", "상품명", "기본/최고금리"]])

st.markdown("---")

# ==========================================
# 6. 하단 AI 투자 비서 챗봇
# ==========================================
st.subheader("🤖 AI 투자 방향 추천 비서")
st.write("투자 목적, 준비된 자금, 선호하는 위험도(예: '시드머니 5,000만원으로 안정적인 투자 방법 추천해줘')를 자유롭게 질문해 보세요.")

# 세션 상태 초기화 (대화 기록 유지)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 통합 금융/자산 데이터를 바탕으로 맞춤형 포트폴리오를 제안해 드립니다. 자금 규모나 포트폴리오 고민을 말씀해주세요."}
    ]

# 이전 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력 처리
if user_prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # AI 응답 세뮬레이션 (실제 구현 시 OpenAI / Gemini API 호출)
    with st.chat_message("assistant"):
        with st.spinner("최신 주식, 부동산, 금리 데이터를 분석 중입니다..."):
            
            # 간단한 규칙 기반 키워드 맞춤 응답 예시 (확장 가능)
            if "5000" in user_prompt or "5천" in user_prompt or "사회초년생" in user_prompt:
                ai_response = (
                    "**[AI 포트폴리오 추천 제안]**\n\n"
                    "현재 시장 지표와 금리 환경을 종합했을 때, 5,000만 원 자산 기준 추천 배분안입니다:\n\n"
                    "1. **안정 자금 (40% - 2,000만원):**\n"
                    "   - 최고 4.30%를 제공하는 **신한 알쏠 적금** 및 시중은행 고금리 예금 활용\n\n"
                    "2. **절세 및 은퇴 자금 (14% - 700만원):**\n"
                    "   - **IRP 계좌(하나/삼성증권)**에 납입하여 연말정산 세액공제 최대로 활용\n\n"
                    "3. **성장형 자산 (46% - 2,300만원):**\n"
                    "   - 실적 모멘텀이 견조한 **삼성전자, SK하이닉스** 등 반도체 대형주 중심 자산 배분"
                )
            elif "부동산" in user_prompt:
                ai_response = (
                    "**[부동산 시장 관점 분석]**\n\n"
                    "최근 7일간 **서울 강남구(342건)**와 **성남시 분당구(289건)**의 거래량이 크게 반등했습니다.\n"
                    "단기적인 고금리 기조가 이어지고 있으므로 실거주 목적이 아니라면, "
                    "상대적으로 대출 부담이 적은 분양가상한제 적용 지역이나 청약 일정을 먼저 검토하시는 것을 권장합니다."
                )
            else:
                ai_response = (
                    f"질문하신 **'{user_prompt}'**에 대한 분석 결과입니다:\n\n"
                    "현재 나스닥 및 코스피 지수가 상승 흐름에 있으나, 예적금 기준금리가 3.5%~4% 수준을 유지하고 있습니다.\n"
                    "따라서 **[투자금의 50%는 안전자산(예적금/IRP), 50%는 미국/한국 우량주]** 형태의 바벨 전략(Barbell Strategy)을 추천합니다."
                )
            
            st.write(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
