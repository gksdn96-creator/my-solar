import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="부동산 정보 - FinAI", layout="wide")
st.title("🏠 부동산 정보 및 대출 상품 가이드")

# 지도 샘플 데이터 (국토교통부 API 연동 가능 구조)
regions = [
    {"name": "강남구 대치동", "lat": 37.493, "lon": 127.058, "sales": 42, "jeonse": 85, "monthly": 30, "avg_price": "24.5억"},
    {"name": "송파구 잠실동", "lat": 37.512, "lon": 127.082, "sales": 38, "jeonse": 62, "monthly": 24, "avg_price": "19.2억"},
    {"name": "분당구 백현동", "lat": 37.395, "lon": 127.111, "sales": 29, "jeonse": 41, "monthly": 15, "avg_price": "14.8억"},
    {"name": "마포구 아현동", "lat": 37.551, "lon": 126.955, "sales": 21, "jeonse": 35, "monthly": 18, "avg_price": "11.5억"}
]

st.subheader("📍 주요 관심 지역 및 매물 현황")

col_map, col_info = st.columns([6, 4])

# Folium 지도 생성
m = folium.Map(location=[37.500, 127.030], zoom_start=11)

for r in regions:
    popup_text = f"<b>{r['name']}</b><br>평균가: {r['avg_price']}<br>매매: {r['sales']}개 | 전세: {r['jeonse']}개"
    folium.Marker(
        [r["lat"], r["lon"]],
        popup=popup_text,
        tooltip=r["name"]
    ).add_to(m)

with col_map:
    map_data = st_folium(m, width="100%", height=450)

with col_info:
    st.write("### 🏢 지역별 매물 상세")
    selected_region = None
    if map_data and map_data.get("last_object_clicked"):
        click_lat = map_data["last_object_clicked"]["lat"]
        click_lon = map_data["last_object_clicked"]["lng"]
        for r in regions:
            if abs(r["lat"] - click_lat) < 0.01 and abs(r["lon"] - click_lon) < 0.01:
                selected_region = r
                break
    
    if selected_region:
        st.success(f"선택된 지역: **{selected_region['name']}**")
        st.metric("평균 매매 거래가", selected_region['avg_price'])
        c1, c2, c3 = st.columns(3)
        c1.metric("매매 물량", f"{selected_region['sales']} 건")
        c2.metric("전세 물량", f"{selected_region['jeonse']} 건")
        c3.metric("월세 물량", f"{selected_region['monthly']} 건")
    else:
        st.info("지도상의 마커를 클릭하면 상세 매물 수량과 평균가가 표시됩니다.")

st.divider()

# 대출 정보
st.subheader("💳 주택담보대출 & 전월세 대출 가이드")
loan_df = pd.DataFrame({
    "대출 종류": ["주택담보대출 (변동)", "주택담보대출 (고정)", "버팀목 전세대출", "일반 전세자금대출"],
    "최저 금리": ["3.95%", "4.10%", "2.10%", "3.80%"],
    "최고 한도": ["LTV 70% 내", "LTV 70% 내", "최대 2.2억원", "최대 5억원"],
    "주요 취급 은행": ["KB국민, 신한", "하나, 우리", "NH농협, 우리", "시중 주요은행"]
})
st.dataframe(loan_df, hide_index=True, use_container_width=True)
