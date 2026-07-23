import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="경제뉴스 - FinAI", layout="wide")

st.title("📰 영역별 실시간 경제 뉴스")

# 분야별 샘플 뉴스 데이터베이스 (최신순 수집 연동 가능)
NEWS_DATABASE = {
    "증권/주식": [
        {"title": f"코스피, 외국인 매수세에 상승 출발… {i+1}위 종목 강세", "media": "한국경제", "time": f"2026-07-23 09:{50-i:02d}", "url": "https://www.hankyung.com", "summary": "외국인과 기관의 동반 순매수로 인해 지수가 우상향 흐름을 나타내고 있습니다."}
        for i in range(25)
    ],
    "부동산": [
        {"title": f"서울 아파트 거래량 전월 대비 {10+i}% 증가… 매수 심리 회복세", "media": "매일경제", "time": f"2026-07-23 08:{55-i:02d}", "url": "https://www.mk.co.kr", "summary": "선호 단지를 중심으로 매물 소진 속도가 빨라지면서 평균 실거래가가 상승하고 있습니다."}
        for i in range(18)
    ],
    "금융/은행": [
        {"title": f"시중은행 예금 금리 인하 움직임… 투자자들 대안 찾기 {i+1}단계", "media": "연합뉴스", "time": f"2026-07-23 07:{45-i:02d}", "url": "https://www.yna.co.kr", "summary": "기준금리 동결 기조 속에서 주요 은행들의 예적금 우대 금리가 일부 조정되었습니다."}
        for i in range(15)
    ],
    "산업/재계": [
        {"title": f"주요 대기업 글로벌 R&D 투자 확대 선언 ({i+1}차 발표)", "media": "서울경제", "time": f"2026-07-23 06:{30-i:02d}", "url": "https://www.sedaily.com", "summary": "차세대 신성장 동력 확보를 위해 시설 투자 및 인재 채용을 대폭 늘릴 예정입니다."}
        for i in range(12)
    ]
}

# 1. 뉴스 영역(카테고리) 선택
selected_cat = st.tabs(list(NEWS_DATABASE.keys()))

for idx, cat_name in enumerate(NEWS_DATABASE.keys()):
    with selected_cat[idx]:
        articles = NEWS_DATABASE[cat_name]
        
        # 최신순 정렬 (시간 내림차순)
        articles_sorted = sorted(articles, key=lambda x: x['time'], reverse=True)
        
        # 2. 페이지네이션 (1페이지당 10개)
        items_per_page = 10
        total_pages = (len(articles_sorted) - 1) // items_per_page + 1
        
        col_page_sel, _ = st.columns([2, 8])
        with col_page_sel:
            current_page = st.selectbox(
                "페이지 이동", 
                range(1, total_pages + 1), 
                key=f"page_{cat_name}"
            )
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_articles = articles_sorted[start_idx:end_idx]
        
        st.write(f"총 **{len(articles_sorted)}**건 중 **{start_idx+1}~{min(end_idx, len(articles_sorted))}**번째 기사")
        st.divider()

        # 3. 뉴스 기사 노출 (10개)
        for news in page_articles:
            st.markdown(f"#### [{news['title']}]({news['url']})")
            st.caption(f"출처: **{news['media']}** | 작성시간: {news['time']}")
            st.write(news['summary'])
            st.link_button("원본 기사 보기 ↗", news['url'])
            st.write("---")
