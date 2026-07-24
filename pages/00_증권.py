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
    .favorite-btn { margin-right: 5px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. 종합 종목명 <-> 티커 한글 매핑 사전
# ----------------------------------------------------
STOCK_NAME_MAP = {
    # 대표 국내 주식
    "삼성전자": "005930.KS", "삼성전자우": "005935.KS",
    "SK하이닉스": "000660.KS", "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS", "현대차": "005380.KS",
    "기아": "000270.KS", "셀트리온": "068270.KS",
    "KB금융": "105560.KS", "신한지주": "055550.KS",
    "POSCO홀딩스": "005490.KS", "NAVER": "035420.KS", "네이버": "035420.KS",
    "카카오": "035720.KS", "삼성전기": "009150.KS",
    "현대모비스": "012330.KS", "LG화학": "051910.KS",
    "삼성SDI": "006400.KS", "한미반도체": "042700.KS",
    "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
    "알테오젠": "196170.KQ", "HLB": "028300.KQ",
    
    # 대표 해외 주식
    "엔비디아": "NVDA", "NVIDIA": "NVDA",
    "애플": "AAPL", "Apple": "AAPL",
    "테슬라": "TSLA", "Tesla": "TSLA",
    "마이크로소프트": "MSFT", "Microsoft": "MSFT",
    "알파벳": "GOOGL", "구글": "GOOGL",
    "아마존": "AMZN", "메타": "META",
    "TSMC": "TSM"
}

# 역매핑 (티커 -> 한글 종목명)
TICKER_TO_NAME = {v: k for k, v in STOCK_NAME_MAP.items()}

def resolve_ticker_and_name(query_str):
    """한글명 또는 티커 입력을 분석하여 (티커, 한글/표시종목명) 튜플 반환"""
    query = query_str.strip()
    
    # 1. 한글 매핑에 직접 존재하는 경우
    if query in STOCK_NAME_MAP:
        ticker = STOCK_NAME_MAP[query]
        return ticker, f"{query} ({ticker})"
    
    # 2. 입력이 6자리 숫자(한국 주식코드)인 경우
    if query.isdigit() and len(query) == 6:
        ticker = f"{query}.KS" # 기본 KOSPI
        name = TICKER_TO_NAME.get(ticker, query)
        return ticker, f"{name} ({ticker})"
    
    # 3. 대문자 티커로 입력된 경우
    query_upper = query.upper()
    if query_upper in TICKER_TO_NAME:
        kor_name = TICKER_TO_NAME[query_upper]
        return query_upper, f"{kor_name} ({query_upper})"
    
    # 4. 기타 티커 직접 입력 (예: 005930.KS, NVDA)
    for t_key, name_val in TICKER_TO_NAME.items():
        if t_key.upper() == query_upper:
            return t_key, f"{name_val} ({t_key})"
            
    # 매핑에 없으면 입력값 자체를 티커로 사용
    return query_upper, query_upper

# ----------------------------------------------------
# 2. 영구 즐겨찾기 로직 (favorites.json 모듈)
# ----------------------------------------------------
FAV_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return ["005930.KS", "NVDA", "000660.KS", "009150.KS"]
    return ["005930.KS", "NVDA", "000660.KS", "009150.KS"]

def save_favorites(fav_list):
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(fav_list, f, ensure_ascii=False)

if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

# ----------------------------------------------------
# 3. 1분 단위 데이터 캐싱 함수 (ttl=60)
# ----------------------------------------------------
@st.cache_data(ttl=60)
def fetch_stock_data_1min(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty:
            return None
        return df
    except Exception:
        return None

st.title("📈 실시간 증권 분석 & AI 주기 예측")
st.caption("⚡ 시세 데이터는 1분 단위로 자동 갱신됩니다.")

# Top 라인: 검색 및 즐겨찾기 관리
col_search, col_fav = st.columns([6, 4])

with col_search:
    user_input = st.text_input("🔍 종목명 또는 티커 검색 (예: 삼성전기, 삼성전자, NVDA, 005930)", value="삼성전기")
    
    # 주요 추천 종목 셀렉트 박스
    preset_options = ["직접 검색 입력"] + list(STOCK_NAME_MAP.keys())
    selected_preset = st.selectbox("또는 주요 종목 리스트에서 바로 선택:", preset_options)
    
    if selected_preset != "직접 검색 입력":
        query_target = selected_preset
    else:
        query_target = user_input

    target_symbol, display_name = resolve_ticker_and_name(query_target)

with col_fav:
    st.write("⭐ **내 영구 즐겨찾기 목록**")
    if st.session_state.favorites:
        fav_cols = st.columns(min(len(st.session_state.favorites), 4))
        for idx, fav_ticker in enumerate(st.session_state.favorites):
            # 한글 이름 변환
            fav_disp_name = TICKER_TO_NAME.get(fav_ticker, fav_ticker)
            col_target = fav_cols[idx % len(fav_cols)]
            if col_target.button(f"⭐ {fav_disp_name}", key=f"fav_btn_{fav_ticker}"):
                target_symbol = fav_ticker
                display_name = f"{fav_disp_name} ({fav_ticker})"
    else:
        st.caption("등록된 즐겨찾기가 없습니다.")

st.divider()

# ----------------------------------------------------
# 4. 메인 상세 종목 실시간 시세 및 즐겨찾기 버튼
# ----------------------------------------------------
df = fetch_stock_data_1min(target_symbol)

if df is not None and not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    diff = curr_price - prev_price
    pct = (diff / prev_price) * 100
    is_usd = not target_symbol.endswith(".KS") and not target_symbol.endswith(".KQ")

    unit_str = "원" if not is_usd else "$"
    price_formatted = f"{curr_price:,.0f}원" if not is_usd else f"${curr_price:,.2f}"
    diff_formatted = f"{abs(diff):,.0f}원" if not is_usd else f"${abs(diff):,.2f}"

    col_title, col_fav_toggle = st.columns([8, 2])
    with col_title:
        arrow_icon = "🔺" if diff > 0 else "🔻"
        color_class = "up-tag" if diff > 0 else "down-tag"
        st.markdown(f"## **{display_name}**")
        st.markdown(f"### 현재가: **{price_formatted}** <span class='{color_class}'>{arrow_icon} {diff_formatted} ({pct:+.2f}%)</span>", unsafe_allow_html=True)
        st.caption(f"최종 갱신시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (1분 캐시 라이브)")

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
    # 5. scikit-learn 예측 모델 및 오차율(MAE / MAPE) 계산
    # ----------------------------------------------------
    st.subheader("🤖 AI 주가 예측 & 모델 오차율(Accuracy)")

    df_ml = df[['Close']].dropna().reset_index()
    df_ml['Day'] = np.arange(len(df_ml))
    
    X = df_ml[['Day']]
    y = df_ml['Close']

    split_idx = int(len(df_ml) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    eval_model = LinearRegression()
    eval_model.fit(X_train, y_train)
    y_pred_test = eval_model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred_test)
    mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

    full_model = LinearRegression()
    full_model.fit(X, y)

    last_day = df_ml['Day'].iloc[-1]
    future_days = np.array([last_day + 1, last_day + 7, last_day + 30, last_day + 180]).reshape(-1, 1)
    future_preds = full_model.predict(future_days)

    def fmt_pred(val):
        return f"{val:,.0f}원" if not is_usd else f"${val:,.2f}"

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("1일 후 예측가", fmt_pred(future_preds[0]))
    col_m2.metric("1주일 후 예측가", fmt_pred(future_preds[1]))
    col_m3.metric("1개월 후 예측가", fmt_pred(future_preds[2]))
    col_m4.metric("6개월 후 예측가", fmt_pred(future_preds[3]))

    mae_str = f"{mae:,.0f}원" if not is_usd else f"${mae:,.2f}"
    st.info(f"📊 **AI 모델 과거 검증 오차율**: 평균 절대 오차 **{mae_str}**, 오차율(MAPE): **{mape:.2f}%**")

    # ----------------------------------------------------
    # 6. 주기성(Cyclicality) 탐지 및 다음 주기 예측
    # ----------------------------------------------------
    st.subheader("🔄 주가 주기성 분석 (Cycle Detection)")

    close_vals = df_ml['Close'].values
    detrended = close_vals - full_model.predict(X)
    autocorr = [pd.Series(detrended).autocorr(lag=i) for i in range(1, 90)]
    
    valid_lags = autocorr[10:]
    detected_cycle_days = np.argmax(valid_lags) + 11 if len(valid_lags) > 0 else 20
    
    last_date = df_ml['Date'].iloc[-1]
    next_cycle_date = last_date + timedelta(days=int(detected_cycle_days))

    st.write(f"🔍 감지된 주요 변동 주기: **약 {detected_cycle_days}일 패턴**")
    st.success(f"📅 주기 분석 기반 **다음 주요 변동/반등 예상 시점**: **{next_cycle_date.strftime('%Y-%m-%d')} 경**")

    # ----------------------------------------------------
    # 7. Plotly 차트 (Y축 자유 조절 & 천단위 콤마/원/$ 표기)
    # ----------------------------------------------------
    st.subheader("📉 주가 추이 및 ML 선형 모델 (가로/세로 축 마우스 휠 조절 가능)")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_ml['Date'], 
        y=df_ml['Close'], 
        mode='lines', 
        name='실제 주가'
    ))
    fig.add_trace(go.Scatter(
        x=df_ml['Date'], 
        y=full_model.predict(X), 
        mode='lines', 
        name='AI 추세선', 
        line=dict(dash='dash', color='orange')
    ))
    
    # Y축 포맷팅 설정 (천단위 구분 쉼표 및 단위원/$ 표기)
    y_ticksuffix = "원" if not is_usd else ""
    y_tickprefix = "" if not is_usd else "$"
    
    fig.update_layout(
        title=f"{display_name} 인터랙티브 시세 차트",
        xaxis_title="날짜",
        yaxis_title=f"주가 ({unit_str})",
        xaxis=dict(
            rangeslider=dict(visible=True), 
            type="date",
            fixedrange=False # X축 줌 허용
        ),
        yaxis=dict(
            tickformat=",d" if not is_usd else ",.2f",
            ticksuffix=y_ticksuffix,
            tickprefix=y_tickprefix,
            fixedrange=False # Y축 세로 축 줌/팬 허용
        ),
        hovermode="x unified"
    )

    # scrollZoom True로 X/Y 축 마우스 휠 조절 지원
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

else:
    st.error(f"종목/검색어 `{user_input}`에 대한 시세 데이터를 불러올 수 없습니다. 종목명이나 티커를 확인해 주세요. (예: 삼성전기, 삼성전자, 005930.KS)")
