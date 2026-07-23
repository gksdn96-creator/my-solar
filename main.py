import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests

# ==========================================
# 1. 페이지 설정 및 사이드바 완전 숨김
# ==========================================
st.set_page_config(
    page_title="AI 통합 자산관리 대시보드",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 사이드바 완전 제거 및 UI 스타일링
st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .more-btn-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 실시간 데이터 가져오기 (실제 API 연동 파트)
# ==========================================

# 2-1. 주요 증시 지표 (실시간 연동 기본 틀)
@st.cache_data(ttl=60)  # 60초 단위 캐싱으로 실시간성 확보
def get_realtime_market_index():
    # 실제 운영 시: 야후 파이낸스(yfinance) 또는 한국투자증권 Open API 호출
    # 예시 데이터 반환
    return {
        "코스피": {"val": "2,755.30", "delta": "+12.40 (+0.45%)"},
        "코스닥": {"val": "890.15", "delta": "-3.20 (-0.36%)"},
        "나스닥": {"val": "16,388.24", "delta": "+115.80 (+0.71%)"},
        "USD/KRW": {"val": "1,345.50", "delta": "+4.50 (+0.34%)"}
    }

# 2-2. 네이버 부동산 실거래/단지 정보 가져오기
@st.cache_data(ttl=300)
def get_naver_realestate_data():
    """
    네이버 부동산 내부 모바일 API 요청 함수
    ※ 실제 네이버 서비스 정책에 따라 헤더 세팅이 필요하며, 요청 제약이 있을 수 있습니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 예시: 서울 주요 거래 활발 단지 (위도, 경도, 거래량, 가격)
    # 실제 네이버 부동산 API: https://m.land.naver.com/cluster/clusterList
    complexes = [
        {"name": "반포자이", "lat": 37.5028, "lon": 127.0125, "trade_cnt": 342, "price": "32.5억", "addr": "서울 서초구 반포동"},
        {"name": "파크리오", "lat": 37.5215, "lon": 127.1065, "trade_cnt": 289, "price": "21.0억", "addr": "서울 송파구 신천동"},
        {"name": "마포래미안푸르지오", "lat": 37.5532, "lon": 126.9555, "trade_cnt": 215, "price": "18.2억", "addr": "서울 마포구 아현동"},
        {"name": "시범아파트", "lat": 37.5245, "lon": 126.9320, "trade_cnt": 198, "price": "25.0억", "addr": "서울 영등포구 여의도동"},
        {"name": "분당 파크뷰", "lat": 37.3655, "lon": 127.1088, "trade_cnt": 176, "price": "15.8억", "addr": "경기 성남시 분당구"}
    ]
    return pd.DataFrame(complexes)

# 2-3. 금융상품 요약 정보
@st.cache_data(ttl=3600)
def get_bank_products_summary():
    # 실제 운영 시: 금융감독원 금융상품통합비교 공시 API 연동
    data = {
        "기관/은행": ["KB국민은행", "신한은행", "하나은행", "NH농협", "삼성증권"],
        "상품 유형": ["정기예금", "적금", "IRP (개인형퇴직연금)", "정기예금", "IRP 원리금보장"],
        "상품명": ["KB Star 정기예금", "신한 알쏠 적금", "하나 IRP 자산관리", "NH 올원예금", "삼성 IRP"],
        "기본/최고금리": ["3.55% / 3.65%", "3.70% / 4.30%", "3.40% / 3.80%", "3.50% / 3.60%", "3.65% / 3.90%"]
    }
    return pd.DataFrame(data)

# 2-4. 언론사 출처 및 원본 링크 포함 실시간 뉴스
@st.cache_data(ttl=300)
def get_realtime_news():
    # 실제 운영 시: 네이버 뉴스 API 또는 언론사 RSS 연동
    return [
        {
            "category": "증권",
            "title": "반도체주 강세로 코스피 상승 마감... 외국인 순매수 지속",
            "media": "한국경제",
            "url": "https://www.hankyung.com",
            "time": "10분 전"
        },
        {
            "category": "부동산",
            "title": "서울 주요 권역 거래량 회복세... 강남·마포 중심으로 신고가 속출",
            "media": "매일경제",
            "url": "https://www.mk.co.kr",
            "time": "25분 전"
        },
        {
            "category": "금융/은행",
            "title": "시중은행 예적금 금리 소폭 하락... IRP 절세 혜택 상품 인기",
            "media": "연합뉴스",
            "url": "https://www.yna.co.kr",
            "time": "1시간 전"
        }
    ]

# ==========================================
# 3. 메인 화면 - 상단 타이틀
# ==========================================
st.title("🌐 AI 통합 자산관리 대시보드")
st.caption("실시간 주식, 네이버 부동산 지도, 금융상품 및 뉴스를 바탕으로 AI가 최적의 투자 방향을 제시합니다.")
st.markdown("---")

# ==========================================
# 4. 섹션 1: 주요 시장 지표 & 환율
# ==========================================
col_header1, col_btn1 = st.columns([8, 2])
with col_header1:
    st.subheader("📈 주요 시장 지표 & 환율")
with col_btn1:
    if st.button("증권 더보기 ➔", key="btn_stock"):
        st.switch_page("pages/1_증권.py")

idx_data = get_realtime_market_index()
m1, m2, m3, m4 = st.columns(4)
m1.metric("코스피 (KOSPI)", idx_data["코스피"]["val"], idx_data["코스피"]["delta"])
m2.metric("코스닥 (KOSDAQ)", idx_data["코스닥"]["val"], idx_data["코스닥"]["delta"])
m3.metric("나스닥 (NASDAQ)", idx_data["나스닥"]["val"], idx_data["나스닥"]["delta"])
m4.metric("원/달러 환율", idx_data["USD/KRW"]["val"], idx_data["USD/KRW"]["delta"])

st.markdown("---")

# ==========================================
# 5. 섹션 2 & 3: 부동산 지도 & 은행/IRP 상품
# ==========================================
col_re, col_bank = st.columns(2)

# [왼쪽] 부동산 지도 (네이버 부동산 데이터 기반)
with col_re:
    col_re_h, col_re_b = st.columns([7, 3])
    with col_re_h:
        st.subheader("🗺️ 지난주 거래량 상위 부동산")
    with col_re_b:
        if st.button("부동산 더보기 ➔", key="btn_re"):
            st.switch_page("pages/2_부동산.py")

    df_re = get_naver_realestate_data()
    
    # Folium 지도 생성 (서울 중심)
    m = folium.Map(location=[37.53, 127.02], zoom_start=11)
    
    for _, row in df_re.iterrows():
        popup_html = f"""
        <div style='width:160px;'>
            <b>{row['name']}</b><br>
            주소: {row['addr']}<br>
            거래량: <b>{row['trade_cnt']}건</b><br>
            평균가: {row['price']}
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{row['name']} ({row['trade_cnt']}건)",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

    st_folium(m, width="100%", height=320)

# [오른쪽] 은행 예적금 & IRP 상품
with col_bank:
    col_bk_h, col_bk_b = st.columns([7, 3])
    with col_bk_h:
        st.subheader("🏦 주요 예적금 & IRP 금리")
    with col_bk_b:
        if st.button("금융상품 더보기 ➔", key="btn_bank"):
            st.switch_page("pages/3_금융_은행.py")

    df_bank = get_bank_products_summary()
    st.dataframe(df_bank, use_container_width=True, height=280)

st.markdown("---")

# ==========================================
# 6. 섹션 4: 언론사 출처/링크 실시간 경제 뉴스
# ==========================================
col_nw_h, col_nw_b = st.columns([8, 2])
with col_nw_h:
    st.subheader("📰 실시간 주요 경제 뉴스")
with col_nw_b:
    if st.button("뉴스 더보기 ➔", key="btn_news"):
        st.switch_page("pages/4_경제뉴스.py")

news_list = get_realtime_news()
n_cols = st.columns(len(news_list))

for i, news in enumerate(news_list):
    with n_cols[i]:
        st.markdown(f"**[{news['category']}]** {news['time']}")
        st.markdown(f"[{news['title']}]({news['url']})")
        st.caption(f"출처: {news['media']}")

st.markdown("---")

# ==========================================
# 7. 메인 화면 하단: AI 투자 방향 추천 챗봇
# ==========================================
st.subheader("🤖 AI 투자 방향 추천 비서")
st.write("실시간 자산 데이터와 뉴스를 기반으로 최적의 맞춤형 포트폴리오를 안내해 드립니다.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 현재 시장 지표, 네이버 부동산 거래 흐름, 시중 금리 정보를 기반으로 최적의 투자 방향을 추천해 드립니다. 자금 규모나 관심 자산을 알려주세요."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_prompt := st.chat_input("예: 5천만원으로 예금과 주식을 활용한 투자 전략 알려줘"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("증권, 부동산, 금융 금리 최신 지표 분석 중..."):
            if "부동산" in user_prompt:
                ai_res = "네이버 부동산 기준 최근 **반포자이(342건)**, **파크리오(289건)** 등 주요 단지 거래량이 증가했습니다. 실거주 외의 대출 부담이 큰 신규 매수는 지양하고, 고금리 파킹통장에 자금을 유지하며 3기 신도시 등의 청약을 노리는 전략을 추천합니다."
            elif "5000" in user_prompt or "5천" in user_prompt:
                ai_res = "5,000만 원 자산 기준 추천 포트폴리오입니다:\n\n1. **안정자산 (50% - 2,500만):** 최고 4.30% 적금 및 IRP 절세 계좌 세액공제 한도 가입\n2. **성장자산 (50% - 2,500만):** 반포/송파 부동산 거래 반등에 따른 수혜가 예상되는 건설/반도체 대형주 중심 자산 분산"
            else:
                ai_res = f"입력하신 **'{user_prompt}'**에 대한 분석입니다.\n\n현재 코스피가 2,700선을 상회하고 있으므로 위험 자산 비중은 40~50% 수준으로 조율하시고, 나머지는 금리 3.8% 이상의 IRP 및 예적금 상품에 분산 배치하는 바벨 전략이 유리합니다."
            
            st.write(ai_res)
            st.session_state.messages.append({"role": "assistant", "content": ai_res})
