import streamlit as st
import pandas as pd

st.set_page_config(page_title="은행 상품 - FinAI", layout="wide")

st.title("🏦 은행 종합 금융 상품 정보")
st.caption("예적금, IRP 뿐만 아니라 대출, 펀드, 외화예금 등 전 종합 금융 상품을 검색하세요.")

# 종합 상품 데이터베이스
BANK_PRODUCTS = {
    "정기예금": [
        {"은행": "KB국민은행", "상품명": "KB Star 정기예금", "최고금리": "3.85%", "가입기간": "12개월", "특징": "비대면 전용, 조건 없이 우대"},
        {"은행": "신한은행", "상품명": "신한 S드림 예금", "최고금리": "3.80%", "가입기간": "12개월", "특징": "급여이체 시 추가 우대"},
        {"은행": "K뱅크", "상품명": "코드K 정기예금", "최고금리": "4.00%", "가입기간": "12개월", "특징": "복리 계산 적용"}
    ],
    "적금": [
        {"은행": "신한은행", "상품명": "신한 알쏠 적금", "최고금리": "4.50%", "가입기간": "12개월", "특징": "소액 자금 자유 적립"},
        {"은행": "우리카드/은행", "상품명": "우리 첫거래 적금", "최고금리": "7.00%", "가입기간": "12개월", "특징": "첫 거래 고객 특판"}
    ],
    "대출 상품": [
        {"은행": "하나은행", "상품명": "하나 원큐 주택담보대출", "최고금리": "연 3.90%~", "가입기간": "최대 40년", "특징": "비대면 원스톱 대출"},
        {"은행": "KB국민은행", "상품명": "KB 직장인 신용대출", "최고금리": "연 4.35%~", "가입기간": "1년(연장가능)", "특징": "우수기업 직장인 우대"}
    ],
    "IRP/퇴직연금": [
        {"은행": "KB국민은행", "상품명": "KB 개인형 IRP", "최고금리": "연 3.9% (평균수익)", "가입기간": "만 55세 이후", "특징": "세액공제 최대 900만원"},
        {"은행": "신한은행", "상품명": "신한 개인형 IRP", "최고금리": "연 4.1% (평균수익)", "가입기간": "만 55세 이후", "특징": "모바일 개설 시 수수료 면제"}
    ],
    "펀드 / ISA": [
        {"은행": "NH농협은행", "상품명": "NH-Amundi 글로벌 AI 펀드", "최고금리": "수익률 실적연동", "가입기간": "자유", "특징": "글로벌 빅테크 집중 투자"},
        {"은행": "하나은행", "상품명": "하나 중개형 ISA", "최고금리": "비과세 혜택", "가입기간": "3년 이상", "특징": "손익통산 비과세 400만원"}
    ],
    "외화 / 기타": [
        {"은행": "하나은행", "상품명": "밀리언달러 외화적금", "최고금리": "연 5.10% (USD)", "가입기간": "6개월", "특징": "달러 강세 시 환차익 비과세"}
    ]
}

# 상단 검색 및 탭
col_cat, col_kwd = st.columns([4, 6])

with col_cat:
    selected_category = st.radio("상품 카테고리 선택", list(BANK_PRODUCTS.keys()), horizontal=True)

with col_kwd:
    search_keyword = st.text_input("🔍 키워드 검색 (예: KB, 우대, 비대면)", "")

# 데이터 필터링
data_list = BANK_PRODUCTS[selected_category]
if search_keyword:
    filtered_data = [
        item for item in data_list 
        if search_keyword.lower() in item['은행'].lower() 
        or search_keyword.lower() in item['상품명'].lower()
        or search_keyword.lower() in item['특징'].lower()
    ]
else:
    filtered_data = data_list

st.subheader(f"📂 [{selected_category}] 검색 결과 ({len(filtered_data)}건)")
df_display = pd.DataFrame(filtered_data)
st.dataframe(df_display, hide_index=True, use_container_width=True)
