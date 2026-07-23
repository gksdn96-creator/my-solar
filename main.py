import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
import datetime

# -----------------------------------------------------------------------------
# 0. Page Config & Session State Init
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 자산 관리 플랫폼 (증권 & 부동산)",
    page_icon="📈",
    layout="wide"
)

# 즐겨찾기 상태 저장
if 'fav_stocks' not in st.session_state:
    st.session_state.fav_stocks = set()
if 'fav_estates' not in st.session_state:
    st.session_state.fav_estates = set()

# 지도 Zoom/Center 상태 저장
if 'map_center' not in st.session_state:
    st.session_state.map_center = [37.5048, 127.0049]  # 반포 자이 근처 기본값
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 13

# -----------------------------------------------------------------------------
# 1. Dummy Data Setup
# -----------------------------------------------------------------------------
# (1) 주식 데이터 생성 (과거 30일 종가 포함)
np.random.seed(42)
dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30, 0, -1)]

stocks_data = {
    "삼성전자": {"price": 78200, "change": 1200, "pct": 1.56, "market_cap": "466조"},
    "SK하이닉스": {"price": 184500, "change": -2000, "pct": -1.07, "market_cap": "134조"},
    "LG에너지솔루션": {"price": 372000, "change": 0, "pct": 0.00, "market_cap": "87조"},
    "NAVER": {"price": 189500, "change": 3500, "pct": 1.88, "market_cap": "30조"},
    "카카오": {"price": 43200, "change": -500, "pct": -1.14, "market_cap": "19조"},
}

# 과거 주가 추이 생성 (ML 예측용)
stock_history = {}
for code, info in stocks_data.items():
    base_price = info['price']
    noise = np.random.normal(0, base_price * 0.015, 30)
    prices = [int(base_price + sum(noise[i:])) for i in range(30)]
    prices[-1] = info['price'] # 현재가 맞춤
    stock_history[code] = pd.DataFrame({"Date": dates, "Price": prices})

# (2) 부동산 데이터 생성
estate_data = [
    {
        "id": "E1", "name": "반포 자이 아파트", "lat": 37.5048, "lng": 127.0049,
        "sale": 45, "jeonse": 18, "wolse": 7, "avg_price": 3250000000, "area": "84㎡"
    },
    {
        "id": "E2", "name": "아크로리버파크", "lat": 37.5088, "lng": 126.9972,
        "sale": 22, "jeonse": 9, "wolse": 4, "avg_price": 3800000000, "area": "84㎡"
    },
    {
        "id": "E3", "name": "마포래미안푸르지오", "lat": 37.5513, "lng": 126.9554,
        "sale": 60, "jeonse": 30, "wolse": 15, "avg_price": 1850000000, "area": "84㎡"
    },
    {
        "id": "E4", "name": "헬리오시티", "lat": 37.4975, "lng": 127.1072,
        "sale": 110, "jeonse": 55, "wolse": 20, "avg_price": 2050000000, "area": "84㎡"
    }
]

# -----------------------------------------------------------------------------
# 2. UI Layout & Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navigation")
menu = st.sidebar.radio("메뉴 선택", ["📈 증권 정보", "🏠 부동산 정보", "⭐ 내 즐겨찾기"])

# -----------------------------------------------------------------------------
# MENU 1: 증권 정보
# -----------------------------------------------------------------------------
if menu == "📈 증권 정보":
    st.header("📈 증권 시장 현황 및 AI 주가 예측")
    
    # 1. 상단 지수 카드
    col1, col2, col3 = st.columns(3)
    col1.metric("KOSPI", "2,750.32", "▲ 15.20 (+0.56%)", delta_color="normal")
    col2.metric("KOSDAQ", "880.15", "▼ 3.40 (-0.38%)", delta_color="inverse")
    col3.metric("USD/KRW", "1,385.50", "▲ 2.10 (+0.15%)", delta_color="normal")

    st.markdown("---")
    st.subheader("🔥 인기 / 시가총액 상위 종목")

    # 종목 리스트 테이블
    for name, data in stocks_data.items():
        c_fav, c_name, c_price, c_change, c_mcap, c_action = st.columns([0.5, 2, 2, 2, 2, 1.5])
        
        # 즐겨찾기 버튼
        is_fav = name in st.session_state.fav_stocks
        fav_icon = "★" if is_fav else "☆"
        if c_fav.button(fav_icon, key=f"fav_stock_{name}"):
            if is_fav:
                st.session_state.fav_stocks.remove(name)
            else:
                st.session_state.fav_stocks.add(name)
            st.rerun()

        c_name.write(f"**{name}**")
        c_price.write(f"{data['price']:,} 원")
        
        # 상승/하락 연출 (한국 스타일: 상승 🔴▲, 하락 🟢▼)
        if data['change'] > 0:
            c_change.markdown(f"<span style='color:red;'>▲ {data['change']:,} ({data['pct']}%)</span>", unsafe_allow_html=True)
        elif data['change'] < 0:
            c_change.markdown(f"<span style='color:green;'>▼ {abs(data['change']):,} ({data['pct']}%)</span>", unsafe_allow_html=True)
        else:
            c_change.write(f"- 0 (0.00%)")
            
        c_mcap.write(f"시총 {data['market_cap']}")

    st.markdown("---")
    st.subheader("🤖 Scikit-Learn 활용 주가 예측")
    
    selected_stock = st.selectbox("예측 대상 종목 선택", list(stocks_data.keys()))
    df_stock = stock_history[selected_stock]
    
    # ML 모델 학습 (선형 회귀 예시)
    df_stock['Day_Num'] = np.arange(len(df_stock))
    X = df_stock[['Day_Num']]
    y = df_stock['Price']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 향후 5일 예측
    future_days = np.array([[len(df_stock) + i] for i in range(5)])
    future_preds = model.predict(future_days)
    
    pred_df = pd.DataFrame({
        "Day": [f"D+{i+1}" for i in range(5)],
        "Predicted_Price": [int(p) for p in future_preds]
    })

    col_chart, col_pred = st.columns([3, 2])
    with col_chart:
        st.write(f"**{selected_stock} 최근 30일 추이**")
        st.line_chart(df_stock.set_index("Date")["Price"])
        
    with col_pred:
        st.write("**AI (Linear Regression) 5일 후 예상 주가**")
        st.table(pred_df)
        last_price = df_stock['Price'].iloc[-1]
        target_price = pred_df['Predicted_Price'].iloc[-1]
        diff = target_price - last_price
        
        if diff > 0:
            st.success(f"현재가 대비 **+{diff:,}원** 상승 추세로 예상됩니다.")
        else:
            st.warning(f"현재가 대비 **{diff:,}원** 하락 추세로 예상됩니다.")

# -----------------------------------------------------------------------------
# MENU 2: 부동산 정보
# -----------------------------------------------------------------------------
elif menu == "🏠 부동산 정보":
    st.header("🏠 부동산 단지 정보 및 대출 계산기")
    
    # 상단 단지 선택 (선택 시 지도가 해당 지역으로 Zoom)
    selected_estate_name = st.selectbox(
        "단지 바로가기 (선택 시 해당 단지로 최대 확대)",
        ["선택하세요"] + [e["name"] for e in estate_data]
    )
    
    if selected_estate_name != "선택하세요":
        target = next(e for e in estate_data if e["name"] == selected_estate_name)
        st.session_state.map_center = [target["lat"], target["lng"]]
        st.session_state.map_zoom = 17 # 최대 축척 레벨 확대

    # Folium 지도 생성
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
    
    for estate in estate_data:
        popup_html = f"""
        <div style="width:180px">
            <b>{estate['name']}</b><br>
            매매: {estate['sale']}건 | 전세: {estate['jeonse']}건<br>
            평균: {estate['avg_price']/100000000:.1f}억원
        </div>
        """
        folium.Marker(
            [estate["lat"], estate["lng"]],
            popup=popup_html,
            tooltip=estate["name"],
            icon=folium.Icon(color="red", icon="home")
        ).add_to(m)

    # 지도 표시
    map_data = st_folium(m, width="100%", height=400)

    st.markdown("---")
    st.subheader("🏢 단지 상세 및 매물 정보")
    
    for estate in estate_data:
        with st.expander(f"📍 {estate['name']} (평균가: {estate['avg_price']/100000000:.1f}억원)", expanded=True):
            col_info, col_fav = st.columns([5, 1])
            
            with col_info:
                st.write(f"**전용면적:** {estate['area']} | **매매 물량:** {estate['sale']}개 | **전세 물량:** {estate['jeonse']}개 | **월세 물량:** {estate['wolse']}개")
                st.write(f"**평균 거래가:** {estate['avg_price']:,} 원")
            
            with col_fav:
                is_fav = estate["id"] in st.session_state.fav_estates
                if st.button("★ 관심 단지 해제" if is_fav else "☆ 관심 단지 등록", key=f"fav_est_{estate['id']}"):
                    if is_fav:
                        st.session_state.fav_estates.remove(estate["id"])
                    else:
                        st.session_state.fav_estates.add(estate["id"])
                    st.rerun()

    # 주담대 계산기
    st.markdown("---")
    st.subheader("🏦 주택담보대출(주담대) 예상 원리금 계산기")
    
    c_loan1, c_loan2, c_loan3 = st.columns(3)
    property_price = c_loan1.number_input("매매가 (원)", value=1000000000, step=10000000)
    ltv = c_loan2.slider("LTV 적용 비율 (%)", min_value=10, max_value=80, value=50)
    interest_rate = c_loan3.number_input("대출 금리 (%)", value=4.0, step=0.1)
    
    loan_amount = property_price * (ltv / 100)
    monthly_rate = (interest_rate / 100) / 12
    term_years = 30
    n_payments = term_years * 12
    
    # 원리금 균등상환 공식
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    
    st.info(f"""
    * **총 대출 가능 한도:** {loan_amount:,.0f} 원 ({loan_amount/100000000:.1f}억원)
    * **필요 자기자본:** {(property_price - loan_amount):,.0f} 원
    * **월 예상 원리금 (30년 상환 기준):** 약 **{monthly_payment:,.0f} 원**
    """)

# -----------------------------------------------------------------------------
# MENU 3: 즐겨찾기
# -----------------------------------------------------------------------------
elif menu == "⭐ 내 즐겨찾기":
    st.header("⭐ 관심 종목 & 매물 모아보기")
    
    col_s, col_e = st.columns(2)
    
    with col_s:
        st.subheader("📈 관심 주식")
        if not st.session_state.fav_stocks:
            st.write("등록된 관심 주식이 없습니다.")
        else:
            for s_name in st.session_state.fav_stocks:
                s_info = stocks_data[s_name]
                st.write(f"**{s_name}**: {s_info['price']:,}원 ({s_info['pct']}%)")
                
    with col_e:
        st.subheader("🏠 관심 부동산 단지")
        if not st.session_state.fav_estates:
            st.write("등록된 관심 부동산이 없습니다.")
        else:
            for e_id in st.session_state.fav_estates:
                e_info = next(e for e in estate_data if e["id"] == e_id)
                st.write(f"**{e_info['name']}**: 평균 {e_info['avg_price']/100000000:.1f}억원 (매매 {e_info['sale']}건)")
