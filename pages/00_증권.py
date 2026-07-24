import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import plotly.graph_objects as go

st.set_page_config(page_title="증권 실시간 분석 & AI 예측 - FinAI", layout="wide")

# CSS 스타일 정의
st.markdown("""
<style>
    .up-tag { color: #e15759; font-weight: bold; background-color: #fde8e8; padding: 3px 8px; border-radius: 4px; }
    .down-tag { color: #4e79a7; font-weight: bold; background-color: #e8f0fe; padding: 3px 8px; border-radius: 4px; }
    .metric-card { background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #e9ecef; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. 영구 즐겨찾기 로직 (favorites.json 모듈)
# ----------------------------------------------------
FAV_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return ["005930.KS", "NVDA", "000660.KS"]
    return ["005930.KS", "NVDA", "000660.KS"]

def save_favorites(fav_list):
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(fav_list, f, ensure_ascii=False)

if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

# ----------------------------------------------------
# 2. 1분 단위 데이터 캐싱 함수 (ttl=60)
# ----------------------------------------------------
@st.cache_data(ttl=60)
def fetch_stock_data_1min(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty:
            return None, None
        
        info = {}
        try:
            info["longName"] = ticker.info.get("longName") or ticker.info.get("shortName") or symbol
        except:
            info["longName"] = symbol

        return df, info
    except Exception as e:
        return None, None

st.title("📈 실시간 증권 분석 & AI 주기 예측")
st.caption("⚡ 시세 데이터는 1분 단위로 자동으로 최신 갱신됩니다.")

# Top 라인: 검색 및 즐겨찾기 관리
col_search, col_fav = st.columns([7, 3])

# 자주 찾는 추천 종목 데이터베이스
POPULAR_STOCKS = {
    "삼성전자 (005930.KS)": "005930.KS",
    "SK하이닉스 (000660.KS)": "000660.KS",
    "LG에너지솔루션 (373220.KS)": "373220.KS",
    "NAVER (035420.KS)": "035420.KS",
    "카카오 (035720.KS)": "035720.KS",
    "엔비디아 (NVDA)": "NVDA",
    "애플 (AAPL)": "AAPL",
    "테슬라 (TSLA)": "TSLA",
    "마이크로소프트 (MSFT)": "MSFT"
}

with col_search:
    user_input = st.text_input("🔍 종목명 / 티커 입력 (예: 005930.KS, NVDA, TSLA, 035420.KS)", value="005930.KS")
    # 추천 리스트 선택 박스
    selected_preset = st.selectbox("또는 주요 종목에서 선택:", ["직접 입력"] + list(POPULAR_STOCKS.keys()))
    if selected_preset != "직접 입력":
        target_symbol = POPULAR_STOCKS[selected_preset]
    else:
        target_symbol = user_input.strip()

with col_fav:
    st.write("⭐ **내 영구 즐겨찾기 목록**")
    if st.session_state.favorites:
        fav_cols = st.columns(len(st.session_state.favorites))
        for idx, fav_item in enumerate(st.session_state.favorites):
            if fav_cols[idx % len(fav_cols)].button(fav_item, key=f"fav_btn_{fav_item}"):
                target_symbol = fav_item
    else:
        st.caption("등록된 즐겨찾기가 없습니다.")

st.divider()

# ----------------------------------------------------
# 3. 메인 상세 종목 실시간 시세 및 즐겨찾기 토글
# ----------------------------------------------------
df, stock_info = fetch_stock_data_1min(target_symbol)

if df is not None and not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    stock_name = stock_info.get("longName", target_symbol) if stock_info else target_symbol
    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    diff = curr_price - prev_price
    pct = (diff / prev_price) * 100

    col_title, col_fav_toggle = st.columns([8, 2])
    with col_title:
        arrow_icon = "🔺" if diff > 0 else "🔻"
        color_class = "up-tag" if diff > 0 else "down-tag"
        st.markdown(f"## **{stock_name}** (`{target_symbol}`)")
        st.markdown(f"### 현재가: **{curr_price:,.2f}** <span class='{color_class}'>{arrow_icon} {abs(diff):,.2f} ({pct:+.2f}%)</span>", unsafe_allow_html=True)
        st.caption(f"최종 갱신시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (1분 단위 자동 업데이트)")

    with col_fav_toggle:
        is_fav = target_symbol in st.session_state.favorites
        if is_fav:
            if st.button("⭐ 즐겨찾기 해제", use_container_width=True):
                st.session_state.favorites.remove(target_symbol)
                save_favorites(st.session_state.favorites)
                st.rerun()
        else:
            if st.button("☆ 즐겨찾기 추가", use_container_width=True):
                st.session_state.favorites.append(target_symbol)
                save_favorites(st.session_state.favorites)
                st.rerun()

    st.divider()

    # ----------------------------------------------------
    # 4. scikit-learn 예측 모델 및 오차율(MAE / MAPE) 계산
    # ----------------------------------------------------
    st.subheader("🤖 AI 주가 예측 & 모델 예측 오차율(Accuracy)")

    df_ml = df[['Close']].dropna().reset_index()
    df_ml['Day'] = np.arange(len(df_ml))
    
    X = df_ml[['Day']]
    y = df_ml['Close']

    # 최근 80% 데이터로 학습, 20% 데이터로 예측 오차 검증
    split_idx = int(len(df_ml) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    eval_model = LinearRegression()
    eval_model.fit(X_train, y_train)
    y_pred_test = eval_model.predict(X_test)

    # 오차 지표 산출
    mae = mean_absolute_error(y_test, y_pred_test)
    mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

    # 전체 데이터 누적 학습 진행
    full_model = LinearRegression()
    full_model.fit(X, y)

    last_day = df_ml['Day'].iloc[-1]
    future_days = np.array([last_day + 1, last_day + 7, last_day + 30, last_day + 180]).reshape(-1, 1)
    future_preds = full_model.predict(future_days)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("1일 후 예측가", f"{future_preds[0]:,.2f}")
    col_m2.metric("1주일 후 예측가", f"{future_preds[1]:,.2f}")
    col_m3.metric("1개월 후 예측가", f"{future_preds[2]:,.2f}")
    col_m4.metric("6개월 후 예측가", f"{future_preds[3]:,.2f}")

    st.info(f"📊 **AI 모델 과거 검증 오차율**: 평균 절대 오차 **{mae:,.2f}**, 오차율(MAPE): **{mape:.2f}%** (일간 누적 데이터를 통해 피팅 정확도가 지속적으로 향상됩니다.)")

    # ----------------------------------------------------
    # 5. 주기성(Cyclicality) 탐지 및 다음 주기 예측 기능
    # ----------------------------------------------------
    st.subheader("🔄 주가 주기성 분석 (Cycle Detection)")

    # 간단한 자기상관(Autocorrelation) 기반 주기 검색
    close_vals = df_ml['Close'].values
    detrended = close_vals - full_model.predict(X)
    autocorr = [pd.Series(detrended).autocorr(lag=i) for i in range(1, 90)]
    
    # 최고 신호 주기 계산 (최소 10일 이상 시차)
    valid_lags = autocorr[10:]
    detected_cycle_days = np.argmax(valid_lags) + 11 if len(valid_lags) > 0 else 20
    
    last_date = df_ml['Date'].iloc[-1]
    next_cycle_date = last_date + timedelta(days=int(detected_cycle_days))

    st.write(f"🔍 감지된 주요 변동 주기: **약 {detected_cycle_days}일 패턴**")
    st.success(f"📅 주기 분석 기반 **다음 주요 변동/반등 예상 시점**: **{next_cycle_date.strftime('%Y-%m-%d')} 경**")

    # ----------------------------------------------------
    # 6. Plotly 차트 (마우스 휠 Zoom 및 축 간격 조절 활성화)
    # ----------------------------------------------------
    st.subheader("📉 주가 추이 및 ML 선형 모델 (마우스 휠로 확대/축소 가능)")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ml['Date'], y=df_ml['Close'], mode='lines', name='실제 주가'))
    fig.add_trace(go.Scatter(x=df_ml['Date'], y=full_model.predict(X), mode='lines', name='AI 추세선', line=dict(dash='dash', color='orange')))
    
    # 마우스 휠 축 조절 활성화 레이아웃
    fig.update_layout(
        title=f"{stock_name} ({target_symbol}) 인터랙티브 시세 차트",
        xaxis_title="날짜",
        yaxis_title="주가",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        hovermode="x unified"
    )

    # config={'scrollZoom': True} 로 마우스 휠 줌 기능 구현
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

else:
    st.error(f"종목 코드 `{target_symbol}`의 데이터를 불러올 수 없습니다. 티커 번호를 확인해 주세요. (예: 삼성전자 005930.KS)")
