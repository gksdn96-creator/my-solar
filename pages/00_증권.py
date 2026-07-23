import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

st.set_page_config(page_title="증권 정보 - FinAI", layout="wide")
st.title("📈 증권 및 주가 예측 분석")

# 시가총액 상위 대표 종목
TOP_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "애플 (Apple)": "AAPL",
    "엔비디아 (NVIDIA)": "NVDA"
}

selected_stock = st.selectbox("종목을 선택하세요", list(TOP_STOCKS.keys()))
ticker_symbol = TOP_STOCKS[selected_stock]

# 데이터 불러오기
@st.cache_data(ttl=600)
def load_stock_data(symbol):
    df = yf.download(symbol, period="2y")
    return df

df = load_stock_data(ticker_symbol)

if not df.empty:
    # yfinance 데이터 칼럼 정리
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    diff = curr_price - prev_price
    pct = (diff / prev_price) * 100

    # 상승/하락 표시 규칙 (상승: 붉은 삼각, 하락: 녹색 삼각)
    if diff > 0:
        color_code = "color: #e15759;"
        arrow = "🔺"
    else:
        color_code = "color: #4e79a7;"
        arrow = "🔻"

    st.markdown(f"### {selected_stock} ({ticker_symbol})")
    st.markdown(f"## 현재가: **{curr_price:,.2f}** 원/달러 <span style='{color_code}'>{arrow} {abs(diff):,.2f} ({pct:+.2f}%)</span>", unsafe_allow_html=True)

    st.divider()

    # ML 기반 미래 주가 예측 (scikit-learn)
    st.subheader("🤖 Machine Learning (scikit-learn) 기반 주가 예측")
    
    # 데이터 전처리
    df_ml = df[['Close']].dropna().reset_index()
    df_ml['Day'] = np.arange(len(df_ml))
    
    X = df_ml[['Day']]
    y = df_ml['Close']

    model = LinearRegression()
    model.fit(X, y)

    # 미래 날짜 예측 (1일, 7일, 30일, 180일 후)
    last_day = df_ml['Day'].iloc[-1]
    future_days = np.array([last_day + 1, last_day + 7, last_day + 30, last_day + 180]).reshape(-1, 1)
    future_preds = model.predict(future_days)

    pred_df = pd.DataFrame({
        "구분": ["1일 후", "1주일 후", "1개월 후", "6개월 후"],
        "예측 가격": [f"{p:,.2f}" for p in future_preds]
    })
    
    col_chart, col_pred = st.columns([7, 3])
    
    with col_pred:
        st.write("**예측 가격 요약**")
        st.table(pred_df)
        st.caption("※ 머신러닝 추세선(Linear Regression) 기반 예측 수치입니다.")

    with col_chart:
        # Plotly 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_ml['Date'], y=df_ml['Close'], mode='lines', name='실제 주가'))
        
        # 추세선
        trend_line = model.predict(X)
        fig.add_trace(go.Scatter(x=df_ml['Date'], y=trend_line, mode='lines', name='ML 추세선', line=dict(dash='dash', color='orange')))
        
        fig.update_layout(title=f"{selected_stock} 주가 추이 및 ML 예측 추세선", xaxis_title="날짜", yaxis_title="가격")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("주가 데이터를 불러오는데 실패했습니다.")
