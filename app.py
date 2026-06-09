import math
import streamlit as st

# ---------------------------------------------------
# 페이지 설정
# ---------------------------------------------------
st.set_page_config(
    page_title="술찌세이버 - 공정한 술자리 정산",
    page_icon="🥂",
    layout="centered"
)

# ---------------------------------------------------
# 커스텀 CSS
# ---------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #f6f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.stNumberInput input {
    font-size: 16px !important;
}

.result-card-green {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #2ecc71;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 12px;
}

.result-card-amber {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #f39c12;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 12px;
}

.card-title {
    color: #7f8c8d;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
}

.card-value {
    color: #2c3e50;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
}

.name-box {
    background: white;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    border: 1px solid #ecf0f1;
}

.footer-box {
    background: #ffffff;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #ecf0f1;
}

.small-text {
    color: #95a5a6;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 헤더
# ---------------------------------------------------
st.title("🥂 술찌세이버 | 술자리 정산 계산기")
st.caption("술 안 마신 사람도 공평하게. 술자리 정산 계산기")
st.markdown("""
총 결제금액과 주류비를 입력하면
술을 마신 사람과 마시지 않은 사람의 정산 금액을 자동 계산합니다.

✔ 술 안 마신 사람은 덜 내고
✔ 술 마신 사람은 더 내는 공정 정산
""")
st.divider()

# ---------------------------------------------------
# 금액 입력
# ---------------------------------------------------
st.subheader("💰 1. 금액 입력")

col1, col2 = st.columns(2)

with col1:
    total_price = st.number_input(
        "총 결제 금액",
        min_value=0,
        value=181600,
        step=1000
    )

with col2:
    alcohol_price = st.number_input(
        "순수 주류비",
        min_value=0,
        value=50000,
        step=1000
    )

# ---------------------------------------------------
# 인원 입력
# ---------------------------------------------------
st.subheader("👥 2. 참석자 입력")

total_people = st.number_input(
    "총 참석 인원",
    min_value=1,
    value=4,
    step=1
)

drinkers = st.number_input(
    "술 마신 인원",
    min_value=0,
    max_value=total_people,
    value=3,
    step=1
)

# ---------------------------------------------------
# 이름 입력
# ---------------------------------------------------
st.subheader("🧑 3. 참석자 이름")

people = []

for i in range(total_people):

    st.markdown(f"##### 참석자 {i+1}")

    c1, c2 = st.columns([2, 1])

    with c1:
        name = st.text_input(
            f"이름_{i}",
            value=f"참석자{i+1}",
            label_visibility="collapsed"
        )

    with c2:
        drank = st.checkbox(
            "술 마심",
            value=(i < drinkers),
            key=f"drink_{i}"
        )

    people.append({
        "name": name,
        "drank": drank
    })

# ---------------------------------------------------
# 정산 옵션
# ---------------------------------------------------
st.subheader("⚙️ 4. 정산 옵션")

round_option = st.selectbox(
    "정산 단위",
    [
        "원 단위 그대로",
        "10원 단위 올림",
        "100원 단위 올림",
        "1000원 단위 올림"
    ]
)

extra_option = st.selectbox(
    "올림 오차 처리",
    [
        "총무가 부담",
        "술 마신 사람들에게 분배"
    ]
)

# ---------------------------------------------------
# 계산 로직
# ---------------------------------------------------
drinkers_count = sum(1 for p in people if p["drank"])
non_drinkers_count = total_people - drinkers_count

common_price = total_price - alcohol_price

if total_people > 0:
    raw_common = common_price / total_people
else:
    raw_common = 0

if drinkers_count > 0:
    raw_alcohol = alcohol_price / drinkers_count
else:
    raw_alcohol = 0


def apply_rounding(value, option):

    if option == "10원 단위 올림":
        return math.ceil(value / 10) * 10

    elif option == "100원 단위 올림":
        return math.ceil(value / 100) * 100

    elif option == "1000원 단위 올림":
        return math.ceil(value / 1000) * 1000

    return int(value)


results = []

for p in people:

    amount = raw_common

    if p["drank"]:
        amount += raw_alcohol

    final_amount = apply_rounding(amount, round_option)

    results.append({
        "name": p["name"],
        "drank": p["drank"],
        "amount": final_amount
    })

# ---------------------------------------------------
# 총합 보정
# ---------------------------------------------------
current_total = sum(r["amount"] for r in results)
diff = current_total - total_price

if diff > 0:

    if extra_option == "술 마신 사람들에게 분배":

        for r in reversed(results):

            if r["drank"]:
                r["amount"] -= diff
                break

# ---------------------------------------------------
# 결과 출력
# ---------------------------------------------------
st.divider()
st.subheader("📍 최종 정산 결과")

for r in results:

    if r["drank"]:

        st.markdown(f"""
        <div class="result-card-amber">
            <div class="card-title">🍺 술 마신 사람</div>
            <div class="card-value">
                {r["name"]} · {r["amount"]:,}원
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(f"""
        <div class="result-card-green">
            <div class="card-title">🥤 술 안 마신 사람</div>
            <div class="card-value">
                {r["name"]} · {r["amount"]:,}원
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------
# 통계
# ---------------------------------------------------
st.divider()
st.subheader("📊 정산 요약")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("총 인원", f"{total_people}명")

with c2:
    st.metric("음주 인원", f"{drinkers_count}명")

with c3:
    ratio = 0

if total_price > 0:
    ratio = round((alcohol_price / total_price) * 100)

st.metric("주류 비율", f"{ratio}%")

# ---------------------------------------------------
# 공유 문구
# ---------------------------------------------------
share_text = f"""[🥂 술찌세이버 정산 결과]

💰 총 결제 금액: {total_price:,}원
🍺 주류비: {alcohol_price:,}원
🍽️ 공용비: {common_price:,}원

👥 인당 정산 금액
"""

for r in results:

    icon = "🍺" if r["drank"] else "🥤"

    share_text += f"\n{icon} {r['name']}: {r['amount']:,}원"

share_text += f"""

※ {round_option} 적용
오늘도 즐거운 술자리 되세요 🥂
"""

st.divider()
st.subheader("💬 카톡 공유")

st.text_area(
    "복사해서 단톡방에 붙여넣으세요",
    share_text,
    height=260
)

# ---------------------------------------------------
# 푸터
# ---------------------------------------------------
st.markdown("""
<div class="footer-box">
<b>술찌세이버 TIP 🍻</b><br>
술을 적게 마셨다면 눈치 보지 말고 정당하게 덜 내세요.

<br><br>

문의: sooljjisaver@gmail.com

<br><br>

<div class="small-text">
Made with Streamlit
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.expander("개인정보처리방침"):

    st.write("""
    술찌세이버는 회원가입 기능을 제공하지 않으며
    사용자의 개인정보를 저장하지 않습니다.

    서비스 품질 개선을 위해 익명 방문 통계가 수집될 수 있습니다.

    문의:
    sooljjisaver@gmail.com
    """)