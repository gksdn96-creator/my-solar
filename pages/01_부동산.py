import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="부동산 정보", page_icon="🏢", layout="wide")

if st.button("🏠 메인 대시보드로 돌아가기"):
    st.switch_page("main.py")

st.title("🏢 네이버 부동산 실거래가 및 거래량 상세 분석")

complexes = [
    {"name": "반포자이", "lat": 37.5028, "lon": 127.0125, "trade_cnt": 342, "price": "32.5억", "addr": "서울 서초구 반포동"},
    {"name": "파크리오", "lat": 37.5215, "lon": 127.1065, "trade_cnt": 289, "price": "21.0억", "addr": "서울 송파구 신천동"},
    {"name": "마포래미안푸르지오", "lat": 37.5532, "lon": 126.9555, "trade_cnt": 215, "price": "18.2억", "addr": "서울 마포구 아현동"}
]

df = pd.DataFrame(complexes)

col1, col2 = st.columns([6, 4])
with col1:
    m = folium.Map(location=[37.52, 127.00], zoom_start=12)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['name']} - {row['price']}",
            tooltip=row['name']
        ).add_to(m)
    st_folium(m, width="100%", height=500)

with col2:
    st.subheader("지역별 상세 목록")
    st.dataframe(df[["name", "addr", "trade_cnt", "price"]], use_container_width=True)
