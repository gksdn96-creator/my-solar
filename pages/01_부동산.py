import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="부동산 매물 정보 - FinAI", layout="wide")

st.title("🏠 부동산 위치 기반 통합 매물 조회")
st.caption("좌측 지도에서 지역 마커를 선택하면 오른쪽에서 즉시 해당 지역의 [매매/전세/월세] 모든 등록 매물이 표시됩니다.")

# 통합 부동산 데이터베이스
REAL_ESTATE_DB = {
    "서울시 강남구 대치동": {
        "lat": 37.493, "lon": 127.058, "avg_price": "24.5억",
        "sales": [
            {"단지명": "선경아파트 101동", "면적": "84㎡", "층수": "12층", "매매가": "25.0억", "등록일": "2026-07-20"},
            {"단지명": "한보미도맨션 203동", "면적": "114㎡", "층수": "8층", "매매가": "29.8억", "등록일": "2026-07-21"},
            {"단지명": "래미안대치팰리스 105동", "면적": "59㎡", "층수": "18층", "매매가": "21.5억", "등록일": "2026-07-22"}
        ],
        "jeonse": [
            {"단지명": "선경아파트 102동", "면적": "84㎡", "층수": "5층", "전세가": "12.5억", "등록일": "2026-07-19"},
            {"단지명": "래미안대치팰리스 102동", "면적": "84㎡", "층수": "15층", "전세가": "15.0억", "등록일": "2026-07-23"}
        ],
        "monthly": [
            {"단지명": "대치 아이파크", "면적": "59㎡", "층수": "3층", "보증금/월세": "1억 / 350만", "등록일": "2026-07-18"}
        ]
    },
    "서울시 송파구 잠실동": {
        "lat": 37.512, "lon": 127.082, "avg_price": "19.2억",
        "sales": [
            {"단지명": "잠실엘스 110동", "면적": "84㎡", "층수": "21층", "매매가": "21.0억", "등록일": "2026-07-22"},
            {"단지명": "리센츠 205동", "면적": "84㎡", "층수": "14층", "매매가": "20.5억", "등록일": "2026-07-23"}
        ],
        "jeonse": [
            {"단지명": "트리지움 302동", "면적": "59㎡", "층수": "9층", "전세가": "9.5억", "등록일": "2026-07-20"}
        ],
        "monthly": [
            {"단지명": "잠실엘스 104동", "면적": "84㎡", "층수": "7층", "보증금/월세": "2억 / 280만", "등록일": "2026-07-21"}
        ]
    },
    "경기도 성남시 분당구 백현동": {
        "lat": 37.395, "lon": 127.111, "avg_price": "14.8억",
        "sales": [
            {"단지명": "판교푸르지오그랑블", "면적": "97㎡", "층수": "11층", "매매가": "18.5억", "등록일": "2026-07-22"}
        ],
        "jeonse": [
            {"단지명": "판교붓들마을 9단지", "면적": "84㎡", "층수": "6층", "전세가": "8.5억", "등록일": "2026-07-19"}
        ],
        "monthly": []
    }
}

col_map, col_list = st.columns([5, 5])

with col_map:
    st.subheader("📍 지도에서 관심 지역 선택")
    
    m = folium.Map(location=[37.495, 127.065], zoom_start=11)

    for name, data in REAL_ESTATE_DB.items():
        total_cnt = len(data["sales"]) + len(data["jeonse"]) + len(data["monthly"])
        popup_html = f"""
        <div style="font-family: Arial; width: 170px;">
            <b>{name}</b><br>
            평균가: {data['avg_price']}<br>
            총 등록매물: {total_cnt}건
        </div>
        """
        folium.Marker(
            [data["lat"], data["lon"]],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{name} (매물 {total_cnt}건)"
        ).add_to(m)

    map_out = st_folium(m, width="100%", height=520)

# 선택된 지역 감지
selected_region = "서울시 강남구 대치동" # 기본값

if map_out and map_out.get("last_object_clicked"):
    click_lat = map_out["last_object_clicked"]["lat"]
    click_lon = map_out["last_object_clicked"]["lng"]
    for name, data in REAL_ESTATE_DB.items():
        if abs(data["lat"] - click_lat) < 0.01 and abs(data["lon"] - click_lon) < 0.01:
            selected_region = name
            break

with col_list:
    st.subheader(f"🏢 [{selected_region}] 상세 매물 목록")
    
    region_info = REAL_ESTATE_DB[selected_region]
    st.success(f"**{selected_region}** 평균 매매가: **{region_info['avg_price']}**")

    # 매매 / 전세 / 월세 매물 일괄 표시
    st.markdown("### 🏢 매매 목록")
    if region_info["sales"]:
        st.dataframe(pd.DataFrame(region_info["sales"]), hide_index=True, use_container_width=True)
    else:
        st.caption("등록된 매매 매물이 없습니다.")

    st.markdown("### 🏠 전세 목록")
    if region_info["jeonse"]:
        st.dataframe(pd.DataFrame(region_info["jeonse"]), hide_index=True, use_container_width=True)
    else:
        st.caption("등록된 전세 매물이 없습니다.")

    st.markdown("### 🔑 월세 목록")
    if region_info["monthly"]:
        st.dataframe(pd.DataFrame(region_info["monthly"]), hide_index=True, use_container_width=True)
    else:
        st.caption("등록된 월세 매물이 없습니다.")

st.divider()

st.subheader("💳 관련 대출 금리 안내")
loan_df = pd.DataFrame({
    "대출 분류": ["주택담보대출", "버팀목 전세대출", "일반 전세자금대출"],
    "최저 금리": ["3.85%", "2.10%", "3.75%"],
    "한도": ["LTV/DSR 기준", "최대 2.2억원", "최대 5억원"]
})
st.dataframe(loan_df, hide_index=True, use_container_width=True)
