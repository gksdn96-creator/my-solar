import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. 페이지 설정 및 사이드바 내비게이션만 숨김
# ==========================================
st.set_page_config(
    page_title="AI 통합 자산관리 대시보드",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 사이드바 전체 숨김이 아닌, 사이드바 내부 UI 요소 및 페이지 내비게이션 메뉴만 제거
st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] {
        width: 0px !important;
        min-width: 0px !important;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 실시간/통합 데이터 로드 함수
# ==========================================

@st.cache_data(ttl=60)
def get_realtime_market_index():
    return {
        "코스피": {"val": "2,755.30", "delta": "+12.40 (+0.45%)"},
        "코스닥": {"val": "890.15", "delta": "-3.20 (-0.36%)"},
        "나스닥": {"val": "16,388.24", "delta": "+115.80 (+0.71%)"},
        "USD/KRW": {"val": "1,345.50", "delta": "+4.50 (+0.34%)"}
    }

@st.cache_data(ttl=300)
def get_nationwide_realestate_data():
    # 수도권 및 전국 주요 거점 실거래 활발 지역 데이터
    complexes = [
        {"name": "반포자이", "lat": 37.5028, "lon": 127.0125, "trade_cnt": 342, "price": "32.5억", "addr": "서울 서초구 반포동"},
        {"name": "파크리오", "lat": 37.5215, "lon": 127.1065, "trade_cnt": 289, "price": "21.0억", "addr": "서울 송파구 신천동"},
        {"name": "마포래미안푸르지오", "lat": 37.5532, "lon": 126.9555, "trade_cnt": 215, "price": "18.2억", "addr": "서울 마포구 아현동"},
        {"name": "삼익비치", "lat": 35.1378, "lon": 129.1165, "trade_cnt": 195, "price": "14.5억", "addr": "부산 수영구 남천동"},
        {"name": "수성범어W", "lat": 35.8589, "lon": 128.6254, "trade_cnt": 182, "price": "12.8억", "addr": "대구 수성구 범어동"},
        {"name": "대전아이파크시티", "lat": 36.3421, "lon": 127.3381, "trade_cnt": 160, "price": "9.2억", "addr": "대전 유성구 상대동"},
        {"name": "봉선남해오네뜨", "lat": 35.1234, "lon": 126.9112, "trade_cnt": 145, "price": "8.1억", "addr": "광주 남구 봉선동"}
    ]
    df = pd.DataFrame(complexes)
    df.index = range(1, len(df) + 1)  # 인덱스 1부터 시작
    return df

@st.cache_data(ttl=3600)
def get_top_bank_products():
    # 예적금, IRP, 대출, 펀드 등 종합 금융 상품 (2년 수익률/최고금리 기준)
    data = [
        {"기관/은행": " 미래에셋증권", "상품 유형": "펀드", "상품명": "미래에셋 미국Tech TOP10", "2년 수익률/금리": "48.50%", "비고": "2년 누적 수익률"},
        {"기관/은행": "삼성자산운용", "상품 유형": "펀드", "상품명": "KODEX 미국 S&P500 TR", "2년 수익률/금리": "32.10%", "비고": "2년 누적 수익률"},
        {"기관/은행": "신한은행", "상품 유형": "적금", "상품명": "신한 알쏠 적금", "2년 수익률/금리": "4.30%", "비고": "최고 연 금리"},
        {"기관/은행": "삼성증권", "상품 유형": "IRP", "상품명": "삼성 IRP 원리금보장", "2년 수익률/금리": "3.90%", "비고": "연 최고 수익률"},
        {"기관/은행": "KB국민은행", "상품 유형": "대출", "상품명": "KB Star 주택담보대출", "2년 수익률/금리": "3.85%", "비고": "최저 최우대 금리"}
    ]
    df = pd.DataFrame(data)
    df.index = range(1, len(df) + 1)  # 인덱스 1부터 시작
    return df

@st.cache_data(ttl=300)
def get_realtime_news():
    return [
        {"category": "증권", "title": "반도체주 강세로 코스피 상승 마감... 외국인 순매수 지속", "media": "한국경제", "url": "https://www.hankyung.com", "time": "10분 전"},
        {"category": "부동산", "title": "전국 주요 거점 아파트 거래량 회복세... 지방 핵심지 신고가 재개", "media": "매일경제", "url": "https://www.mk.co.kr", "time": "25분 전"},
        {"category": "금융/은행", "title": "2년간 ETF·펀드 수익률 고공행진... 은행권 맞춤형 IRP 상품 출시", "media": "연합뉴스", "url": "https://www.yna.co.kr", "time": "1시간 전"}
    ]

# ==========================================
# 3. 메인 화면 헤더
# ==========================================
st.title("🌐 AI 통합 자산관리 대시보드")
st.caption("실시간 주식, 전국 부동산 지도, 수익률 상위 금융상품 및 경제 뉴스를 한눈에 확인하세요.")
st.markdown("---")

# ==========================================
# 4. 섹션 1: 주요 시장 지표 & 환율
# ==========================================
col_header1, col_btn1 = st.columns([8, 2])
with col_header1:
    st.subheader("📈 주요 시장 지표 & 환율")
with col_btn1:
    if st.button("증권 더보기 ➔", key="btn_stock"):
        st.switch_page("pages/00_증권.py")

idx_data = get_realtime_market_index()
m1, m2, m3, m4 = st.columns(4)
m1.metric("코스피 (KOSPI)", idx_data["코스피"]["val"], idx_data["코스피"]["delta"])
m2.metric("코스닥 (KOSDAQ)", idx_data["코스닥"]["val"], idx_data["코스닥"]["delta"])
m3.metric("나스닥 (NASDAQ)", idx_data["나스닥"]["val"], idx_data["나스닥"]["delta"])
m4.metric("원/달러 환율", idx_data["USD/KRW"]["val"], idx_data["USD/KRW"]["delta"])

st.markdown("---")

# ==========================================
# 5. 섹션 2 & 3: 전국 부동산 지도 & Top 5 금융상품
# ==========================================
col_re, col_bank = st.columns(2)

with col_re:
    col_re_h, col_re_b = st.columns([7, 3])
    with col_re_h:
        st.subheader("🗺️ 전국 거래량 상위 부동산")
    with col_re_b:
        if st.button("부동산 더보기 ➔", key="btn_re"):
            st.switch_page("pages/01_부동산.py")

    df_re = get_nationwide_realestate_data()
    
    # 대한민국 전역이 보이도록 중심점 및 Zoom 조정 (Zoom: 7)
    m = folium.Map(location=[36.0, 127.8], zoom_start=7)
    
    for _, row in df_re.iterrows():
        popup_html = f"<b>{row['name']}</b><br>{row['addr']}<br>거래량: <b>{row['trade_cnt']}건</b><br>매매가: {row['price']}"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{row['name']} ({row['trade_cnt']}건)",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

    st_folium(m, width="100%", height=310)

with col_bank:
    col_bk_h, col_bk_b = st.columns([7, 3])
    with col_bk_h:
        st.subheader("🏆 2년 수익률/금리 Top 5 금융상품")
    with col_bk_b:
        if st.button("은행/금융 더보기 ➔", key="btn_bank"):
            st.switch_page("pages/02_은행.py")

    df_bank = get_top_bank_products()
    st.dataframe(df_bank, use_container_width=True, height=310)

st.markdown("---")

# ==========================================
# 6. 섹션 4: 실시간 경제 뉴스
# ==========================================
col_nw_h, col_nw_b = st.columns([8, 2])
with col_nw_h:
    st.subheader("📰 실시간 주요 경제 뉴스")
with col_nw_b:
    if st.button("뉴스 더보기 ➔", key="btn_news"):
        st.switch_page("pages/03_경제뉴스.py")

news_list = get_realtime_news()
n_cols = st.columns(len(news_list))

for i, news in enumerate(news_list):
    with n_cols[i]:
        st.markdown(f"**[{news['category']}]** {news['time']}")
        st.markdown(f"[{news['title']}]({news['url']})")
        st.caption(f"출처: **{news['media']}**")

st.markdown("---")

# ==========================================
# 7. AI 투자 비서 챗봇
# ==========================================
st.subheader("🤖 AI 투자 방향 추천 비서")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 전국 부동산 거래량, 수익률 상위 펀드/대출/예적금 데이터와 지표를 바탕으로 맞춤형 포트폴리오를 추천합니다. 질문을 입력해주세요."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        ai_res = f"입력하신 **'{user_prompt}'**에 대한 분석 결과입니다.\n\n현재 2년간 높은 성과를 낸 미국 IT 펀드(수익률 40% 이상)와 3.8% 이상의 안정적인 예적금/IRP 자산을 5:5 비율로 조합하는 자산 배분 전략을 추천합니다."
        st.write(ai_res)
        st.session_state.messages.append({"role": "assistant", "content": ai_res})
