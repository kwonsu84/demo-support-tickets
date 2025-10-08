import datetime
import random
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# 페이지 설정: 제목, 아이콘, 레이아웃(화면 전체 너비 사용)
st.set_page_config(
    page_title="Support tickets",
    page_icon="🎫",
    layout="wide"   # wide: 화면 전체 너비 사용
)

# 앱 제목 표시
st.title("🎫 Support tickets")

# 앱 소개 문구
st.write(
    """
    이 앱은 Streamlit으로 만든 내부 지원 티켓 관리 도구 예제입니다.
    사용자는 티켓을 생성하고, 수정하며, 통계 정보를 확인할 수 있습니다.
    """
)

# --- 기존 티켓(샘플 데이터) 생성 ---
if "df" not in st.session_state:  # 세션에 데이터프레임이 없을 경우만 실행

    np.random.seed(42)  # 난수 고정 (재현성 확보)

    # 가짜 이슈 설명(문제 내용) 목록
    issue_descriptions = [
        "사무실 네트워크 연결 문제",
        "소프트웨어 실행 시 충돌 발생",
        "프린터 응답 없음",
        "이메일 서버 다운",
        "데이터 백업 실패",
        "로그인 인증 문제",
        "웹사이트 속도 저하",
        "보안 취약점 발견",
        "서버 하드웨어 오류",
        "공유폴더 접근 불가",
        "데이터베이스 연결 실패",
        "모바일 앱 동기화 오류",
        "VoIP 전화 시스템 문제",
        "원격 근무자 VPN 접속 문제",
        "시스템 업데이트 호환성 문제",
        "파일 서버 저장공간 부족",
        "침입 탐지 시스템 경고",
        "재고관리 시스템 오류",
        "CRM 고객 데이터 로딩 실패",
        "협업툴 알림 전송 안 됨",
    ]

    # 100개의 가짜 티켓 데이터 생성
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],  # 티켓 번호
        "Issue": np.random.choice(issue_descriptions, size=100),  # 이슈 내용
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),  # 상태
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),  # 우선순위
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],  # 제출일
    }
    df = pd.DataFrame(data)

    # 세션 상태(session_state)에 데이터 저장 (앱 재실행 시에도 유지됨)
    st.session_state.df = df


# --- 새 티켓 추가 영역 ---
st.header("Add a ticket")  # 섹션 제목

# 폼(form) 내부에서 입력 위젯 구성
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")  # 문제 설명 입력
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])  # 우선순위 선택
    submitted = st.form_submit_button("Submit")  # 제출 버튼

# 폼 제출 시 실행
if submitted:
    # 새로운 티켓 데이터 생성 후 기존 데이터에 추가
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")

    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # 제출 완료 메시지 + 새 티켓 미리보기
    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)

    # 새 티켓을 기존 데이터프레임 위쪽에 추가
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)


# --- 기존 티켓 목록 및 수정 영역 ---
st.header("Existing tickets")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")  # 티켓 수 표시

st.info(
    "표에서 셀을 더블클릭하면 내용을 직접 수정할 수 있습니다. "
    "아래 그래프는 수정 내용에 따라 자동으로 갱신됩니다. "
    "컬럼 제목을 클릭하면 정렬도 가능합니다.",
    icon="✍️",
)

# 티켓 표 표시 (수정 가능)
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(  # 상태 선택 가능
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(  # 우선순위 선택 가능
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    disabled=["ID", "Date Submitted"],  # ID와 제출일은 수정 불가
)


# --- 통계 정보 표시 ---
st.header("Statistics")

# 3개의 지표를 가로로 나란히 표시
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)


# --- Altair 차트로 시각화 ---
st.write("")
st.write("##### Ticket status per month")  # 월별 상태별 티켓 수

status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",  # 제출월
        y="count():Q",                # 티켓 수
        xOffset="Status:N",           # 상태별로 분리
        color="Status:N",             # 상태별 색상
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

# 우선순위별 비율(원형 차트)
st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")  # 우선순위별 비율
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
