import streamlit as st
import pandas as pd

st.set_page_config(page_title="은행 상품 - FinAI", layout="wide")
st.title("🏦 은행 예적금 & IRP 상품 비교")

tab1, tab2, tab3 = st.tabs(["정기예금", "적금", "IRP (개인형 퇴직연금)"])

with tab1:
    st.subheader("💡 정기예금 금리 Top 5")
    deposit_df = pd.DataFrame({
        "은행": ["K뱅크", "카카오뱅크", "KB국민은행", "신한은행", "하나은행"],
        "상품명": ["코드K 정기예금", "카카오 정기예금", "KB Star 정기예금", "신한 S드림 예금", "하나 하나의정기예금"],
        "기본금리": ["3.80%", "3.70%", "3.50%", "3.55%", "3.60%"],
        "최고금리": ["4.00%", "3.80%", "3.85%", "3.85%", "3.90%"],
        "만기": ["12개월", "12개월", "12개월", "12개월", "12개월"]
    })
    st.dataframe(deposit_df, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("🔥 주요 적금 상품")
    saving_df = pd.DataFrame({
        "은행": ["신한은행", "우리카드/은행", "NH농협은행", "IBK기업은행"],
        "상품명": ["신한 알쏠 적금", "우리 첫거래 적금", "NH올원 적금", "IBK 탄탄 적금"],
        "최고금리": ["4.50%", "7.00%", "4.20%", "4.00%"],
        "월 납입한도": ["50만원", "30만원", "100만원", "50만원"]
    })
    st.dataframe(saving_df, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("🛡️ IRP(개인형 퇴직연금) 수수료 및 수익률")
    irp_df = pd.DataFrame({
        "금융사": ["미래에셋증권", "삼성증권", "KB국민은행", "신한투자증권"],
        "수수료": ["비대면 개설 시 무료", "비대면 개설 시 무료", "연 0.2%", "비대면 개설 시 무료"],
        "최근 1년 평균 수익률": ["6.2%", "5.8%", "4.1%", "5.5%"]
    })
    st.dataframe(irp_df, hide_index=True, use_container_width=True)
