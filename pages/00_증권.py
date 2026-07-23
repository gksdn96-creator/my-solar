import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

st.set_page_config(page_title="증권 정보 - FinAI", layout="wide")

# Custom CSS for badging and standard stock market styling
st.markdown("""
<style>
    .up-tag { color: #e15759; font-weight: bold; background-color: #fde8e8; padding: 3px 8px; border-radius: 4px; }
    .down-tag { color: #4e79a7; font-weight: bold; background-color: #e8f0fe; padding: 3px 8px; border-radius: 4px; }
    .action-buy { font-weight: bold; color: white; background-color: #d9534f; padding: 6px 12px; border-radius: 6px; display: inline-block; }
    .action-hold { font-weight: bold; color: white; background-color: #f0ad4e; padding: 6px 12px; border-radius: 6px; display: inline-block; }
    .action-sell { font-weight: bold; color: white; background-color: #0275d8; padding: 6px 12px; border-radius: 6px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.title("📈 국내외 증권 종목 검색 및 AI 분석")

# 업종/테마별 종목 DB
STOCK_DATABASE = {
    "반도체/IT": {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", 
        "엔비디아 (NVDA)": "NVDA", "TSMC (TSM)": "TSM"
    },
    "2차전지/배터리": {
        "LG에너지솔루션": "373220.KS", "POSCO홀딩스": "005490.KS", "삼성SDI": "006400.KS", 
        "에코프로비엠": "247540.KQ", "테슬라 (TSLA)": "TSLA"
    },
    "제약/바이오": {
        "삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "유한양행": "000100.KS", "일양약품": "007570.KS"
    },
    "자동차/운송": {
        "현대차": "005380.KS", "기아": "000270.KS", "현대모비스": "012330.KS"
    },
    "플랫폼/인터넷": {
        "NAVER": "035420.KS", "카카오": "035720.KS", "알파벳 (GOOGL)": "GOOGL", "마이크로소프트 (MSFT)": "MSFT"
    }
}

# 1. 업종/테마별 종목 리스트 테이블
st.subheader("📂 테마/업종별 종목 현황")

col_theme, col_search = st.columns([4, 6])
with col_theme:
    selected_theme = st.selectbox("테마/업종 선택", list(STOCK_DATABASE.keys()))

theme_stocks = STOCK_DATABASE[selected_theme]

@st.cache_data(ttl=300)
def fetch_theme_summary(stocks_dict):
    rows = []
    for name, ticker in stocks_dict.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                diff = curr - prev
                pct = (diff / prev) * 100
                arrow = "🔺" if diff > 0 else ("🔻" if diff < 0 else "➖")
                diff_str = f"{arrow} {abs(diff):,.2f}"
                rows.append({
                    "종목명": name,
                    "티커": ticker,
                    "현재가": f"{curr:,.2f}",
                    "전일비": diff_str,
                    "등락률": f"{pct:+.2f}%",
                    "_raw_diff": diff
                })
        except:
            pass
    return pd.DataFrame(rows)

summary_df = fetch_theme_summary(theme_stocks)
if not summary_df.empty:
    disp_df = summary_df.drop(columns=["_raw_diff"])
    st.dataframe(disp_df, hide_index=True, use_container_width=True)

st.divider()

# 2. 상장 종목 상세 검색 및 예측 분석
st.subheader("🔍 종목 상세 분석 & AI 투자 가이드")

all_stocks = {}
for theme, stocks in STOCK_DATABASE.items():
    all_stocks.update(stocks)

selected_stock_name = st.selectbox("상세 분석할 종목을 선택하거나 티커를 검색하세요", list(all_stocks.keys()))
ticker_symbol = all_stocks[selected_stock_name]

@st.cache_data(ttl=600)
def load_stock_detail(symbol):
    df = yf.download(symbol, period="1y")
    return df

df = load_stock_detail(ticker_symbol)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    diff = curr_price - prev_price
    pct = (diff / prev_price) * 100

    col_val, col_guide = st.columns([5, 5])

    with col_val:
        arrow_icon = "🔺" if diff > 0 else "🔻"
        color_class = "up-tag" if diff > 0 else "down-tag"
        st.markdown(f"### {selected_stock_name} (`{ticker_symbol}`)")
        st.markdown(f"## **{curr_price:,.2f}** <span class='{color_class}'>{arrow_icon} {abs(diff):,.2f} ({pct:+.2f}%)</span>", unsafe_allow_html=True)

    # ML 모델 학습 (scikit-learn)
    df_ml = df[['Close']].dropna().reset_index()
    df_ml['Day'] = np.arange(len(df_ml))
    X = df_ml[['Day']]
    y = df_ml['Close']

    model = LinearRegression()
    model.fit(X, y)

    last_day = df_ml['Day'].iloc[-1]
    future_days = np.array([last_day + 1, last_day + 7, last_day + 30, last_day + 180]).reshape(-1, 1)
    future_preds = model.predict(future_days)

    pred_1m_change = ((future_preds[2] - curr_price) / curr_price) * 100
    pred_6m_change = ((future_preds[3] - curr_price) / curr_price) * 100

    # AI 보유/추가매수/손절 추천 로직
    with col_guide:
        st.markdown("#### 🤖 AI 추천 대응 전략")
        if pred_6m_change > 10 and pred_1m_change > 0:
            action_badge = "<span class='action-buy'>🔥 강력 추가 매수 (Strong Buy)</span>"
            guide_msg = "단기 및 중장기 상승 추세가 매우 견고합니다. 보유 중이라면 유지하고, 미보유 시 추가 매수를 적극 고려할 수 있습니다."
        elif pred_6m_change > 0:
            action_badge = "<span class='action-hold'>⏸️ 계속 보유 (Hold)</span>"
            guide_msg = "완만한 우상향 추세를 보이고 있습니다. 급격한 추세 전환 전까지는 손절 없이 관망하며 보유를 유지하세요."
        elif pred_6m_change > -10:
            action_badge = "<span class='action-hold'>⚠️ 일부 분할 매도 / 관망 (Caution)</span>"
            guide_msg = "단기 조정 가능성이 존재합니다. 비중을 축소하거나 현금 비중을 확보하는 것을 권장합니다."
        else:
            action_badge = "<span class='action-sell'>🚨 손절 / 위험 관리 (Stop Loss)</span>"
            guide_msg = "하락 추세 모멘텀이 강합니다. 추가 손실 방지를 위해 손절매 또는 비중 확 줄이기를 고려해야 하는 구간입니다."

        st.markdown(action_badge, unsafe_allow_html=True)
        st.caption(guide_msg)

    # 예측 가격표 및 차트
    st.write("---")
    col_chart, col_pred_table = st.columns([7, 3])

    with col_pred_table:
        st.write("**AI 기간별 예측 주가**")
        pred_df = pd.DataFrame({
            "구분": ["1일 후", "1주일 후", "1개월 후", "6개월 후"],
            "예측가": [f"{p:,.2f}" for p in future_preds],
            "예측 변동률": [f"{((p-curr_price)/curr_price)*100:+.2f}%" for p in future_preds]
        })
        st.table(pred_df)

    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_ml['Date'], y=df_ml['Close'], mode='lines', name='실제 주가'))
        trend_line = model.predict(X)
        fig.add_trace(go.Scatter(x=df_ml['Date'], y=trend_line, mode='lines', name='ML 추세선', line=dict(dash='dash', color='orange')))
        fig.update_layout(title=f"{selected_stock_name} 주가 추이 및 예측 선형 모델", xaxis_title="날짜", yaxis_title="가격")
        st.plotly_chart(fig, use_container_width=True)
