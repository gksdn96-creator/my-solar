import streamlit as st
import pandas aspd

st.set_page_config(page_title="금융/은행 정보", page_icon="🏦", layout="wide")

if st.button("🏠 메인 대시보드로 돌아가기"):
    st.switch_page("main.py")

st.title("🏦 전국 은행 예적금 및 IRP 금리 비교")

data = {
    "기관/은행": ["KB국민은행", "신한은행", "하나은행", "NH농협", "삼성증권"],
    "상품 유형": ["정기예금", "적금", "IRP (개인형퇴직연금)", "정기예금", "IRP 원리금보장"],
    "상품명": ["KB Star 정기예금", "신한 알쏠 적금", "하나 IRP 자산관리", "NH 올원예금", "삼성 IRP"],
    "기본/최고금리": ["3.55% / 3.65%", "3.70% / 4.30%", "3.40% / 3.80%", "3.50% / 3.60%", "3.65% / 3.90%"]
}

st.dataframe(pd.DataFrame(data), use_container_width=True)
