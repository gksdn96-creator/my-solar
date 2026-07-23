import streamlit as st
import pandas as pd

st.set_page_config(page_title="증권 상세 정보", page_icon="📈", layout="wide")

if st.button("🏠 메인 대시보드로 돌아가기"):
    st.switch_page("main.py")

st.title("📈 국내/해외 주식 상세 정보")

stocks = [
    {"종목명": "삼성전자", "코드": "005930", "현재가": 78500, "등락률": "+1.2%", "PER": 14.2, "추천도": "매수"},
    {"종목명": "SK하이닉스", "코드": "000660", "현재가": 178000, "등락률": "+2.8%", "PER": 21.5, "추천도": "강력매수"},
    {"종목명": "NAVER", "코드": "035420", "현재가": 189500, "등락률": "-0.8%", "PER": 28.1, "추천도": "보유"},
    {"종목명": "엔비디아 (NVDA)", "코드": "NVDA", "현재가": "$892.10", "등락률": "+3.4%", "PER": 65.2, "추천도": "매수"},
    {"종목명": "애플 (AAPL)", "코드": "AAPL", "현재가": "$172.50", "등락률": "-0.2%", "PER": 26.8, "추천도": "보유"}
]

st.dataframe(pd.DataFrame(stocks), use_container_width=True)
