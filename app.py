import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(page_title="전고체전지 분석 챗봇", layout="centered")

# -----------------------------
# 2. 스타일
# -----------------------------
st.markdown("""
<style>
body { font-family: 'Noto Sans KR', sans-serif; }
.stButton>button { 
    width: 100%; background-color: #37b5a5; color: #fff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. 세션 상태
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 4. 인증
# -----------------------------
if not st.session_state.authenticated:
    st.title("🔒 Solid-State Battery Analyst")

    password = st.text_input("Password", type="password")

    if st.button("접속"):
        if password == "grsi":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호 오류")

    st.stop()

# -----------------------------
# 5. 사이드바
# -----------------------------
with st.sidebar:
    st.write("전고체전지 기사 URL 분석 챗봇")
    if st.button("초기화"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# 6. API 설정
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API KEY 오류")
    st.stop()

# -----------------------------
# 7. 기사 크롤링 함수
# -----------------------------
def get_article_text(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # 스크립트 제거
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        return "\n".join(lines)[:5000]  # 토큰 제한
    except Exception as e:
        return f"크롤링 실패: {e}"

# -----------------------------
# 8. 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """당신은 전고체전지 산업 수석 애널리스트입니다.

반드시 아래 형식으로 작성:
- 한국 대기업 보고서 스타일 (~임, ~함)

[분석]
1. 핵심 요약 (5줄)
2. 주요 키워드
3. 파급력 분석 (큼/중간/작음)
4. 인사이트
"""

# -----------------------------
# 9. 모델 생성
# -----------------------------
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# -----------------------------
# 10. 기존 대화 출력
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 11. 입력 처리
# -----------------------------
if prompt := st.chat_input("URL 또는 질문 입력"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):

            try:
                # URL이면 크롤링
                if "http" in prompt:
                    article = get_article_text(prompt)

                    if "크롤링 실패" in article:
                        full_prompt = prompt
                    else:
                        full_prompt = f"""
다음 기사 내용을 분석하라:

{article}
"""
                else:
                    full_prompt = prompt

                response = model.generate_content(full_prompt)

                # 안전한 출력
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

# -----------------------------
# 12. 푸터
# -----------------------------
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:12px;'>Battery Analyst Bot</div>",
    unsafe_allow_html=True
)
