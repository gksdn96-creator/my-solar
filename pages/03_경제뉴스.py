import streamlit as st

st.set_page_config(page_title="카테고리별 경제 뉴스", page_icon="📰", layout="wide")

if st.button("🏠 메인 대시보드로 돌아가기"):
    st.switch_page("main.py")

st.title("📰 카테고리별 실시간 경제 뉴스")

cat = st.selectbox("뉴스 영역 선택", ["전체", "증권/주식", "부동산", "금융/은행"])

news_items = [
    {"category": "증권/주식", "title": "반도체주 강세로 코스피 상승 마감... 외국인 순매수 지속", "media": "한국경제", "url": "https://www.hankyung.com", "desc": "외국인 투자자들의 반도체 섹터 집중 매수가 이어지며 지수 상승을 견인했습니다."},
    {"category": "부동산", "title": "서울 주요 권역 거래량 회복세... 강남·마포 중심으로 신고가 속출", "media": "매일경제", "url": "https://www.mk.co.kr", "desc": "아파트 거래량이 전월 대비 20% 증가하며 급매물이 소진되고 있습니다."},
    {"category": "금융/은행", "title": "시중은행 예적금 금리 소폭 하락... IRP 절세 혜택 상품 인기", "media": "연합뉴스", "url": "https://www.yna.co.kr", "desc": "금리 인하 기대감에 따라 장기 고금리 상품으로 자금이 몰리는 추세입니다."}
]

for item in news_items:
    if cat == "전체" or cat == item["category"]:
        with st.container():
            st.markdown(f"### [{item['category']}] [{item['title']}]({item['url']})")
            st.caption(f"언론사: **{item['media']}**")
            st.write(item["desc"])
            st.markdown("---")
