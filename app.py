import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석 챗봇", layout="centered")

# 스타일
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stButton>button { background-color: #37b5a5; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 상태
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 인증
if not st.session_state.authenticated:
    pw = st.text_input("Password", type="password")
    if st.button("접속"):
        if pw == "grsi":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호 오류")
    st.stop()

# 4. 사이드바
with st.sidebar:
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# 5. API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API KEY 오류")
    st.stop()

# 6. 시스템 프롬프트
SYSTEM_PROMPT = """당신은 전고체전지 산업 수석 애널리스트임.
반드시 한국 대기업 보고서 스타일(~임, ~함)로 작성.

[분석]
1. 핵심 요약 (5줄)
2. 주요 키워드
3. 파급력 분석
4. 인사이트
"""

# 7. 모델 생성 (안정 버전)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-latest",
    system_instruction=SYSTEM_PROMPT
)

# 8. 기존 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. 입력 처리
if prompt := st.chat_input("URL 또는 질문 입력"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            try:
                # ✅ 핵심: chat + history 적용
                chat = model.start_chat(history=[])

                for msg in st.session_state.messages[:-1]:  # 현재 입력 제외
                    role = "user" if msg["role"] == "user" else "model"
                    chat.history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

                response = chat.send_message(prompt)

                # 안전 출력
                try:
                    answer = response.text
                except:
                    answer = response.candidates[0].content.parts[0].text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"에러 발생: {e}")

# 10. 푸터
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:12px;'>Battery Analyst Bot</div>",
    unsafe_allow_html=True
)
