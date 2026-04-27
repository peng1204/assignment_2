import streamlit as st
import json
import random

# 1. 페이지 설정
st.set_page_config(
    page_title="전자레인지 안전 지능 테스트",
    page_icon="😶‍🌫️",
    layout="centered"
)
# 2. 데이터 로드(캐싱)
# -----------------------------
@st.cache_data
def load_security_db():
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def get_random_quiz(data):
    return random.sample(data, 10) if len(data) >= 10 else data

# 3. 세션 상태 초기화
# -----------------------------
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "GATE"

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "final_score" not in st.session_state:
    st.session_state.final_score = 0

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

if "survey_data" not in st.session_state:
    st.session_state.survey_data = {}

if "diagnostic_data" not in st.session_state:
    st.session_state.diagnostic_data = []

# 4. 사이드바
# -----------------------------
with st.sidebar:
    st.header("내 정보")

    if st.session_state.auth_status:
        st.success(f"{st.session_state.user_name}님")

        if st.button("로그아웃"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.cache_data.clear()
            st.rerun()
    else:
        st.warning("로그인이 필요해요")

    st.divider()
    st.caption("Kitchen Safety Intelligence v1.2")

# page1. 메인 화면
# -----------------------------
if st.session_state.current_stage == "GATE":
    st.title("😶‍🌫️ 내 전자레인지 안전 지능은?")
    st.markdown("### 무심코 돌렸다가 '펑' 할 수도 있어요!")

    st.info("""
    - 학번: 2021508036
    - 이름: 김현진
    """)

    st.write("우리 집 주방을 안전하게 지키고 있나요? 평소 습관을 분석하고 안전 지능 점수를 확인해보세요.")

    if st.button("시작하기", use_container_width=True):
        st.session_state.current_stage = "AUTH"
        st.rerun()

# page2. 로그인 화면
# -----------------------------
elif st.session_state.current_stage == "AUTH":
    st.title("🔐 로그인을 해주세요")
    st.write("안전 보고서에 기록될 정보를 입력해주세요.")

    with st.container(border=True):
        name_input = st.text_input("이름", placeholder="예: 홍길동")
        id_input = st.text_input("학번", placeholder="학번 10자리를 입력해주세요")

        if st.button("로그인하기", use_container_width=True):
            if not name_input.strip():
                st.error("이름을 적어주세요.")
            elif not id_input.strip() or not id_input.isdigit() or len(id_input) < 8:
                st.error("학번을 다시 확인해주세요.")
            else:
                st.session_state.auth_status = True
                st.session_state.user_name = name_input
                st.session_state.current_stage = "SURVEY"
                st.rerun()

# page3. 사전 설문 화면
# -----------------------------
elif st.session_state.current_stage == "SURVEY":
    st.title("📊 평소 습관이 궁금해요")
    st.write(f"**{st.session_state.user_name}**님의 주방 라이프스타일을 알려주세요.")

    with st.form("survey_form"):
        freq = st.select_slider(
            "1. 일주일에 전자레인지를 얼마나 쓰시나요?",
            options=["거의 안 씀", "1~2번", "3~5번", "매일"]
        )

        check_mark = st.radio(
            "2. 음식을 돌리기 전 '전자레인지용' 표시를 확인하시나요?",
            ["항상 확인한다", "가끔 확인한다", "확인해본 적 없다"]
        )

        main_food = st.multiselect(
            "3. 자주 데워 드시는 음식은 무엇인가요? (중복 선택 가능)",
            ["냉동식품", "남은 배달 음식", "편의점 도시락", "직접 한 요리"]
        )

        if st.form_submit_button("테스트 시작하기"):
            st.session_state.survey_data = {
                "freq": freq,
                "check_mark": check_mark,
                "main_food": main_food
            }

            # 퀴즈 시작 시점에 문제를 한 번만 랜덤 추출해서 세션에 저장
            all_data = load_security_db()
            st.session_state.diagnostic_data = get_random_quiz(all_data)

            st.session_state.current_stage = "DIAGNOSIS"
            st.rerun()

# page4. 퀴즈 화면
# -----------------------------
elif st.session_state.current_stage == "DIAGNOSIS":
    diagnostic_data = st.session_state.diagnostic_data

    st.title("🍱 돌리면 어떻게 될까요?")
    st.write("10가지 상황을 보고 안전한지 판단해주세요.")
    st.write("---")

    with st.form("diagnosis_form"):
        current_answers = []

        for i, item in enumerate(diagnostic_data):
            st.markdown(f"**{i + 1}. {item['question']}**")

            ans = st.radio(
                "선택지",
                item["options"],
                key=f"q{i}",
                index=None,
                label_visibility="collapsed"
            )

            current_answers.append(ans)
            st.write("")
            st.divider()

        if st.form_submit_button("채점하기", use_container_width=True):
            if None in current_answers:
                st.error("아직 고르지 않은 문제가 있어요!")
            else:
                score = sum(
                    1 for i, q in enumerate(diagnostic_data)
                    if current_answers[i] == q["answer"]
                )

                st.session_state.final_score = score
                st.session_state.user_logs = current_answers
                st.session_state.current_stage = "REPORT"
                st.rerun()

# page5. 결과 보고서 화면
# -----------------------------
elif st.session_state.current_stage == "REPORT":
    diagnostic_data = st.session_state.diagnostic_data

    st.title("📋 안전 지능 성적표")

    tab1, tab2, tab3 = st.tabs(["✨ 종합 분석", "🔍 오답 노트", "💡 맞춤 솔루션"])

    with tab1:
        score = st.session_state.final_score

        if score == 10:
            type_title = "🏅 완벽한 살림꾼"
            type_desc = "주방의 평화를 수호하는 자! 당신의 지식은 완벽해요."
            st.balloons()
        elif score >= 7:
            type_title = "👏 무사안일주의자"
            type_desc = "괜찮아요, 하지만 한두 번의 실수로 집을 태울 뻔했네요!"
        elif score >= 4:
            type_title = "🚧 자취 초보 빌런"
            type_desc = "전자레인지와 아직 내외하는 중인가요? 좀 더 친해져봐요."
        else:
            type_title = "🚨 주방의 연금술사"
            type_desc = "무엇이든 폭발시키는 능력자! 전자레인지 사용 금지령이 시급해요."

        st.metric("내 안전 지능", f"{score * 10}점", f"{score}/10")
        st.subheader(f"유형: {type_title}")
        st.write(type_desc)

        st.divider()
        st.write("**카테고리별 성취도**")

        categories = list(set([d["category"] for d in diagnostic_data]))

        for cat in categories:
            cat_total = sum(1 for d in diagnostic_data if d["category"] == cat)

            cat_correct = sum(
                1 for i, d in enumerate(diagnostic_data)
                if d["category"] == cat and st.session_state.user_logs[i] == d["answer"]
            )

            st.progress(
                cat_correct / cat_total,
                text=f"{cat} (정답 {cat_correct}/{cat_total})"
            )

    with tab2:
        st.subheader("틀린 문제 다시보기")

        wrong_count = 0

        for i, item in enumerate(diagnostic_data):
            user_ans = st.session_state.user_logs[i]
            is_right = user_ans == item["answer"]

            if not is_right:
                wrong_count += 1

                with st.expander(f"❌ {item['question']}"):
                    st.write(f"**내가 고른 답:** {user_ans}")
                    st.write(f"**정답:** {item['answer']}")
                    st.info(f"**해설:** {item['explanation']}")

        if wrong_count == 0:
            st.success("🎉 틀린 문제가 없습니다! 모든 문제를 맞혔어요.")

    with tab3:
        st.subheader(f"{st.session_state.user_name}님을 위한 맞춤 솔루션")

        survey = st.session_state.survey_data
        score = st.session_state.final_score

        # 용기 재질 카테고리에서 오답이 있는지 확인
        container_fail = any(
            d.get("category") == "용기 재질"
            and st.session_state.user_logs[i] != d["answer"]
            for i, d in enumerate(diagnostic_data)
        )

        if score == 10:
            st.success(
                "🏅 **완벽한 주방 안전 습관!**\n"
                "모든 문제를 맞혔어요. 지금처럼 전자레인지용 표시와 재질을 꼼꼼히 확인하는 습관을 유지하면 좋습니다."
            )

        elif survey["check_mark"] == "확인해본 적 없다" and container_fail:
            st.error(
                f"⚠️ **위험 징후 발견!**\n"
                f"평소 용기 확인을 안 하는 습관이 이번 테스트에서도 드러났어요. "
                f"'{survey['main_food'][0] if survey['main_food'] else '배달 음식'}'을 데울 때는 "
                f"용기 바닥의 전자레인지 사용 가능 표시를 꼭 확인해보세요."
            )

        elif survey["freq"] == "매일" and score < 7:
            st.warning(
                "⚠️ **사용량 대비 주의력 부족!**\n"
                "전자레인지를 매일 쓰는 편이지만 안전 지식은 조금 부족한 편이에요. "
                "자주 사용하는 만큼 오늘 배운 내용을 꼭 기억해보세요."
            )

        else:
            st.info(
                "✅ **기본 습관은 괜찮아요!**\n"
                "다만 몇 가지 상황에서는 헷갈릴 수 있으니, 틀린 문제의 해설을 다시 확인해보세요."
            )

        if st.button("처음부터 다시 하기"):
            st.cache_data.clear()

            # 다시 시작할 때 기존 퀴즈 데이터와 답변 초기화
            st.session_state.current_stage = "GATE"
            st.session_state.final_score = 0
            st.session_state.user_logs = []
            st.session_state.survey_data = {}
            st.session_state.diagnostic_data = []

            st.rerun()