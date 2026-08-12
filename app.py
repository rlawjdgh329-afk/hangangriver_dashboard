import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#==============================================================
# 1. 페이지 설정
#==============================================================
st.set_page_config(
    page_title = '한강공원 이용객 분석',
    page_icon = '🌉',
    layout = 'wide'
)

st.title('🌉 한강공원 이용객 분석 대시보드')
st.caption('서울시 한강공원 월별 이용객 데이터를 활용한 이용 패턴 분석')

#=============================================================
# 2. 데이터 불러오기
#=============================================================
@st.cache_data
def load_data():
    df = pd.read_csv(
        '서울시 한강공원 월별 이용객 현황.csv',
        encoding='cp949'
    )

    # 날짜 변환
    df['현황 일시'] = pd.to_datetime(df['현황 일시'])

    # 연도, 월 생성
    df['연도'] = df['현황 일시'].dt.year
    df['월'] = df['현황 일시'].dt.month

    # 계절 생성
    def get_season(month):
        if month in [3,4,5]:
            return '봄'
        elif month in [6,7,8]:
            return '여름'
        elif month in [9,10,11]:
            return '가을'
        else:
            return '겨울'

    df["계절"] = df['월'].apply(get_season)

    # 분석에 사용할 숫자 컬럼
    numeric_cols = [
        "일반이용자(아침)",
        "일반이용자(낮)",
        "일반이용자(저녁)",
        "자전거",
        "인라인",
        "pm(개인형이동장치)",
        "주요행사",
        "마라톤",
        "운동시설",
        "야구장",
        "수상시설",
        "수영장/물놀이장",
        "캠핑장",
        "음악분수",
        "키즈랜드",
        "장미원",
        "세빛섬",
        "물빛광장",
        "골프장",
        "노들섬",
        "습지생태공원"
    ]

    df[numeric_cols] = df[numeric_cols].fillna(0)

    # 일반 이용객 계산
    df['일반이용객'] = (
        df['일반이용자(아침)']
        + df['일반이용자(낮)']
        + df['일반이용자(저녁)']
    )

    return df

df = load_data()

# 2024년은 2월까지만 있으므로 연간 비교에서는 제외
analysis_df = df[df["연도"] < 2024]

#===============================================
# 3. KPI
#===============================================

st.subheader('📌핵심 지표')

total_users = analysis_df['일반이용객'].sum()

park_yearly = (
    analysis_df
    .groupby(['연도','공원명'])['일반이용객']
    .sum()
    .reset_index()
)

park_avg = (
    park_yearly
    .groupby('공원명')['일반이용객']
    .mean()
)

top_park = park_avg.idxmax()

monthly_users = (
    analysis_df
    .groupby(['연도','월'])['일반이용객']
    .sum()
    .reset_index()
)

monthly_avg = (
    monthly_users
    .groupby('월')['일반이용객']
    .mean()
)

top_month = monthly_avg.idxmax()

season_users = (
    analysis_df
    .groupby(['연도','계절'])['일반이용객']
    .sum()
    .reset_index()
)

season_avg = (
    season_users
    .groupby('계절')['일반이용객']
    .mean()
)

top_season = season_avg.idxmax()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        '누적 이용객',
        f"{total_users:,.0f}명"
    )

with col2:
    st.metric(
        '최다 이용 공원',
        top_park
    )

with col3:
    st.metric(
        '최다 이용월',
        f"{top_month}월"
    )

with col4:
    st.metric(
        '최다 이용 계절',
        top_season
    )

st.divider()

#================================================
# 4. 연도별 분석
#================================================
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.subheader("📊 연도별 이용객 변화")

yearly_users = (
    analysis_df
    .groupby('연도')['일반이용객']
    .sum()
    .reset_index()
)

fig1, ax1 = plt.subplots(figsize = (8,5))

sns.barplot(
    data=yearly_users,
    x='연도',
    y='일반이용객',
    ax=ax1
)

ax1.set_title('연도별 한강공원 이용객 수')
ax1.set_xlabel('연도')
ax1.set_ylabel('이용객 수')

st.pyplot(fig1)

st.info(
    '2018년 이후 이용객이 감소하는 흐름이 나타났으며,'
    '2022년 가장 낮은 수준을 기록한 후 2023년 다시 증가하는 모습을 보였습니다.'
)

#==============================================
# 5. 월별 / 계절별 분석
#==============================================
st.subheader("📅 월별·계절별 이용 패턴")

col1, col2 = st.columns(2)

with col1 :
    monthly_avg_df = monthly_avg.reset_index()

    fig2, ax2 = plt.subplots(figsize=(8,5))

    sns.lineplot(
        data=monthly_avg_df,
        x='월',
        y='일반이용객',
        marker='o',
        ax=ax2
    )

    ax2.set_title('월별 평균 이용객 수')
    ax2.set_xlabel('월')
    ax2.set_ylabel('평균 이용객 수')
    ax2.set_xticks(range(1,13))

    st.pyplot(fig2)

    st.caption(
        '4~5월 이용객이 가장 높은 수준을 보이며.'
        '여름철 감소 후 10월 다시 증가하고 겨울철에 크게 감소하는 패턴이 나타납니다.'
    )

with col2:
    season_order = ['봄','여름','가을','겨울']

    season_avg_df = season_avg.reset_index()

    fig3, ax3 = plt.subplots(figsize=(8,5))

    sns.barplot(
        data=season_avg_df,
        x='계절',
        y='일반이용객',
        order=season_order,
        ax = ax3
    )

    ax3.set_title("계절별 평균 이용객 수")
    ax3.set_xlabel("계절")
    ax3.set_ylabel("평균 이용객 수")

    st.pyplot(fig3)

    st.caption(
        "봄철 이용객이 가장 많고 겨울철이 가장 적어 "
        "한강공원 이용에 뚜렷한 계절적 차이가 나타납니다."
    )


st.divider()

#==================================================
# 6. 공원별 이용객 분석
#==================================================
st.subheader('📍 공원별 이용객 비교')

park_avg_df = (
    park_avg
    .sort_values(ascending=False)
    .reset_index()
)

fig4, ax4 = plt.subplots(figsize =(10,6))

sns.barplot(
    data=park_avg_df,
    x='일반이용객',
    y='공원명',
    ax = ax4
)

ax4.set_title("공원별 연평균 이용객 수")
ax4.set_xlabel("연평균 이용객 수")
ax4.set_ylabel("공원명")

st.pyplot(fig4)

st.info(
    "뚝섬한강공원이 가장 높은 이용객을 기록했으며, "
    "여의도와 반포한강공원이 뒤를 이었습니다. "
    "공원별 이용 규모의 차이가 크게 나타납니다."
)


st.divider()

#============================================
# 7. 인기 공원 시설, 활동 분석
#============================================
st.subheader("🏞️ 인기 한강공원 주요 활동·시설 분석")

facility_cols = [
    "자전거",
    "운동시설",
    "장미원",
    "음악분수",
    "키즈랜드",
    "주요행사",
    "물빛광장",
    "마라톤",
    "세빛섬",
    "수상시설"
]

select_park = st.selectbox(
    '공원을 선택하세요',
    ['뚝섬한강공원','여의도한강공원','반포한강공원']
)

park_detail = analysis_df[
    analysis_df['공원명'] == select_park
]

park_facility = (
    park_detail[facility_cols]
    .sum()
    .sort_values(ascending = False)
)

# 이용량 0 제외
park_facility = park_facility[park_facility > 0].head(5)

park_facility_df = park_facility.reset_index()
park_facility_df.columns = ['활동/시설','이용객']

fig5,ax5 = plt.subplots(figsize = (9,5))

sns.barplot(
    data=park_facility_df,
    x='이용객',
    y='활동/시설',
    ax = ax5
)

ax5.set_title(f"{select_park} 주요 활동·시설 이용 현황")
ax5.set_xlabel("누적 이용객 수")
ax5.set_ylabel("활동·시설")

st.pyplot(fig5)

#=========================================================
# 8. 공원별 인사이트
#=========================================================
if select_park == '뚝섬한강공원':
    st.success(
        "뚝섬은 자전거와 운동시설 이용량이 매우 높으며, "
        "장미원·음악분수·키즈랜드 등 다양한 여가시설 이용도 활발합니다."
    )
elif select_park == "여의도한강공원":
    st.success(
        "여의도는 자전거 이용과 함께 주요행사 이용량이 높으며, "
        "물빛광장과 마라톤 등 행사·야외활동 중심의 이용 특성이 나타납니다."
    )

elif select_park == "반포한강공원":
    st.success(
        "반포는 자전거 이용량과 세빛섬 이용량이 특히 높아, "
        "자전거·랜드마크 시설 중심의 이용 특성이 두드러집니다."
    )


st.divider()

#=======================================================
# 9. 분석 결론
#=======================================================

st.subheader('💡 분석 결론')

st.write(
    """
    한강공원 이용객은 월별·계절별·공원별로 뚜렷한 차이를 보였습니다.
    특히 봄철과 4~5월에 이용객이 집중되었으며,
    공원별로는 뚝섬·여의도·반포의 이용 규모가 상대적으로 높게 나타났습니다.

    또한 인기 공원에서도 이용 형태가 서로 달라,
    뚝섬은 운동·레저 중심,
    여의도는 행사·야외활동 중심,
    반포는 세빛섬과 같은 대표시설 중심의 특성을 보였습니다.
    """
)

st.warning(
    "이러한 분석 결과는 성수기 인력 배치, 시설 점검, 안전관리, "
    "청소 인력 운영 등의 우선순위를 결정하는 기초자료로 활용할 수 있습니다."
)