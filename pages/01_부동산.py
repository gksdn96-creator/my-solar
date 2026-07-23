import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="부동산 정보 - FinAI", layout="wide")

st.title("🏠 부동산 지역별 매물 및 대출 정보")

# 부동산 데이터베이스 및 상세 매물 목록
REAL_ESTATE_DATA = {
    "서울시 강남구 대치동": {
        "lat": 37.493, "lon": 127.058, "avg_price": "24.5억",
        "items": {
            "매매": [
                {"단지명": "선경아파트 101동", "면적": "84㎡", "층수": "12층", "가격": "25.0억"},
                {"단지명": "한보미도맨션 203동", "면적": "114㎡", "층수": "8층", "가격": "29.8억"},
                {"단지명": "래미안대치팰리스", "면적": "59㎡", "층수": "18층", "가격": "21.5억"}
            ],
            "전세": [
                {"단지명": "선경아파트 102동", "면적": "84㎡", "층수": "5층", "가격": "12.5억"},
                {"단지명": "래미안대치팰리스", "면적": "84㎡", "층수": "15층", "가격": "15.0억"}
            ],
            "월세": [
                {"단지명": "대치 아이파크", "면적": "59㎡", "층수": "3층", "가격": "1억 / 350만"}
            ]
        }
    },
    "서울시 송파구 잠실동": {
        "lat": 37.512, "lon": 127.082, "avg_price": "19.2억",
        "items": {
            "매매": [
                {"단지명": "잠실엘스 110동", "면적": "84㎡", "층수": "21층", "가격": "21.0억"},
                {"단지명": "리센츠 205동", "면적": "84㎡", "층수": "14층", "가격": "20.5억"}
            ],
            "전세": [
                {"단지명": "트리지움 302동", "면적": "59㎡", "층수": "9층", "가격": "9.5억"}
            ],
            "월세": [
                {"단지명": "잠실엘스 104동", "면적": "84㎡", "층수": "7층", "가격": "2억 / 280만"}
            ]
        }
    },
    "경기도 성남시 분당구 백현동": {
        "lat": 37.395, "lon": 127.111, "avg_price": "14.8억",
        "items": {
            "매매": [
                {"단지명": "판교푸르지오그랑블", "면적": "97㎡", "층수": "11층", "가격": "18.5억"}
            ],
            "전세": [
                {"단지명": "판교붓들마을 9단지", "면적": "84㎡", "층수": "6층", "가격": "8.5억"}
            ],
            "월세": []
        }
    }
}

col_map, col_detail = st.columns([6, 4])

with col_map:
    st.subheader("📍 지도상 지역 선택 (클릭 시 확대)")
    
    # 깔끔한 맵 초기화
    m = folium.Map(location=[37.495, 127.065], zoom_start=11)

    for loc_name, info in REAL_ESTATE_DATA.items():
        sales_cnt = len(info["items"]["매매"])
        jeonse_cnt = len(info["items"]["전세"])
        
        # 깔끔하게 다듬은 HTML 커스텀 팝업
        popup_html = f"""
        <div style="font-family: Arial; width: 180px; padding: 5px;">
            <h4 style="margin:0 0 5px 0; color:#2c3e50;">{loc_name.split()[-1]}</h4>
            <hr style="margin:4px 0;">
            <b>평균가:</b> {info['avg_price']}<br>
            <b>매매:</b> {sales_cnt}건 | <b>전세:</b> {jeonse_cnt}건
        </div>
        """
        folium.Marker(
            [info["lat"], info["lon"]],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{loc_name} (평균 {info['avg_price']})"
        ).add_to(m)

    map_data = st_folium(m, width="100%", height=420)

with col_detail:
    st.subheader("🏢 지역 및 상세 매물 조회")
    
    # 지도 마커 클릭 연동 또는 셀렉트박스 선택
    selected_loc = st.selectbox("조회할 지역을 선택하세요", list(REAL_ESTATE_DATA.keys()))
    
    loc_info = REAL_ESTATE_DATA[selected_loc]
    st.info(f"**{selected_loc}** 평균 거래가: **{loc_info['avg_price']}**")

    # 매물 건수 버튼 선택
    st.write("▼ **물량 유형을 클릭하여 상세 매물을 확인하세요**")
    col_b1, col_b2, col_b3 = st.columns(3)
    
    sales_cnt = len(loc_info["items"]["매매"])
    jeonse_cnt = len(loc_info["items"]["전세"])
    monthly_cnt = len(loc_info["items"]["월세"])

    if "type_filter" not in st.session_state:
        st.session_state["type_filter"] = "매매"

    if col_b1.button(f"🏢 매매 ({sales_cnt}건)"):
        st.session_state["type_filter"] = "매매"
    if col_b2.button(f"🏠 전세 ({jeonse_cnt}건)"):
        st.session_state["type_filter"] = "전세"
    if col_b3.button(f"🔑 월세 ({monthly_cnt}건)"):
        st.session_state["type_filter"] = "월세"

    filter_type = st.session_state["type_filter"]
    st.write(f"#### [{filter_type}] 상세 매물 목록")
    
    item_list = loc_info["items"][filter_type]
    if item_list:
        item_df = pd.DataFrame(item_list)
        st.dataframe(item_df, hide_index=True, use_container_width=True)
    else:
        st.write("해당 조건의 등록된 매물이 없습니다.")

st.divider()

st.subheader("💳 주택담보 및 전월세 대출 금융상품")
loan_data = pd.DataFrame({
    "대출 분류": ["주택담보대출", "주택담보대출", "전세자금대출", "전세자금대출", "신용대출"],
    "상품명": ["KB Star 주택담보대출", "신한 주택담보대출(고정)", "버팀목 전세자금대출", "카카오뱅크 전월세보증금대출", "하나 원큐 신용대출"],
    "금리 유형": ["변동금리", "혼합형(고정)", "변동금리", "변동금리", "변동금리"],
    "최저 금리": ["3.85%", "4.05%", "2.10%", "3.75%", "4.50%"],
    "한도": ["LTV/DSR 범위 내", "LTV/DSR 범위 내", "최대 2.2억원", "최대 5억원", "최대 2.2억원"]
})
st.dataframe(loan_data, hide_index=True, use_container_width=True)
