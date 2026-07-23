import streamlit as st
import pandas as pd

st.set_page_config(page_title="경제뉴스 - FinAI", layout="wide")
st.title("📰 실시간 주요 경제 뉴스")
st.caption("언론사 공식 출처 제공 및 원문 바로가기 지원")

# 네이버 뉴스 API / BigKinds Open API 확장용 데이터
news_list = [
    {
        "title": "한국은행 금리동결 발표… 부동산 시장에 미칠 영향은?",
        "media": "연합뉴스",
        "time": "10분 전",
        "summary": "한국은행 금융통화위원회가 기준금리를 동결함에 따라 시중 대출금리 향방에 관심이 쏠리고 있다.",
        "url": "https://www.yna.co.kr"
    },
    {
        "title": "뉴욕증시, 기술주 강세에 나스닥 최고치 경신",
        "media": "한국경제",
        "time": "30분 전",
        "summary": "AI 반도체 수요 지속으로 주요 기술주가 일쑤 상승하며 지수를 끌어올렸다.",
        "url": "https://www.hankyung.com"
    },
    {
        "title": "서울 아파트 거래량 3개월 연속 상승세… 분당·송파 주도",
        "media": "매일경제",
        "time": "1시간 전",
        "summary": "주요 선호 지역을 중심으로 실수요 매수세가 유입되며 매매 거래량이 점진 회복 중이다.",
        "url": "https://www.mk.co.kr"
    }
]

for news in news_list:
    with st.container():
        st.markdown(f"### [{news['title']}]({news['url']})")
        st.caption(f"출처: **{news['media']}** | {news['time']}")
        st.write(news['summary'])
        st.link_button("원본 기사 읽기 ↗", news['url'])
        st.divider()
