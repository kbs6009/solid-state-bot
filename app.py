import streamlit as st
import google.generativeai as genai
import requests

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석 챗봇", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #333; }
    .title { font-size: 28px; font-weight: 700; color: #000; text-align: center; margin-bottom: 10px; }
    .subtitle { font-size: 15px; color: #666; text-align: center; margin-bottom: 30px; }
    .stButton>button { 
        width: 100%; background-color: #37b5a5; color: #fff; border-radius: 5px; 
        padding: 12px; font-size: 16px; font-weight: 700; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2d9387; color: #fff; }
    .auth-box {
        padding: 40px; border-radius: 10px; border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# URL 본문 추출 함수
def get_article_text(url):
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, timeout=10)
        return response.text[:8000] if response.status_code == 200 else None
    except:
        return None

# 2. 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 인증 로직
if not st.session_state.authenticated:
    st.markdown("<div style='padding-top: 80px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:30px;'><img src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/LG_Energy_Solution_logo.svg/1024px-LG_Energy_Solution_logo.svg.png' width='220'></div>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Solid-State Battery Analyst</div>", unsafe_allow_html=True)
        pw = st.text_input("Password", type="password", placeholder="암호를 입력하세요", label_visibility="collapsed")
        if st.button("접속하기"):
            if pw == "grsi":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호 오류")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. 사이드바
with st.sidebar:
    st.markdown("### **수석 애널리스트 챗봇**")
    st.write("구글 검색 기능을 사용하여 실시간 데이터와 참고 문헌을 분석합니다.")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# 5. API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API KEY 오류. Streamlit Secrets를 확인하세요.")
    st.stop()

# 6. 시스템 프롬프트
SYSTEM_PROMPT = """당신은 전고체전지 산업 수석 애널리스트임.
반드시 한국 대기업 보고서 스타일(~임, ~함)로 작성.

[분석 규칙]
1. 제공된 기사 내용을 기본으로 하되, 부족한 정보(연구자 이력, 기업 최신 동향, 관련 기술 논문 등)는 반드시 '구글 검색'을 통해 보완할 것.
2. 분석 마지막에는 참고한 주요 웹사이트나 논문의 링크를 '참고 문헌'으로 정리할 것.

[분석 양식]
1. 핵심 요약 (5줄)
2. 주요 키워드 및 인물 (검색을 통해 인물 이력 포함)
3. 파급력 분석 (큼/중간/작음)
4. 애널리스트 인사이트 (시장 판도 변화 및 기술적 근거)
5. 🔗 참고 문헌 (검색된 링크 정리)
"""

# 7. 모델 생성 함수 (에러 방지를 위해 함수화)
def get_model(use_search=True):
    if use_search:
        # 최신 구글 검색 도구 설정 방식
        tools = [{"google_search_retrieval": {}}]
        return genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=tools,
            system_instruction=SYSTEM_PROMPT
        )
    else:
        # 검색 도구 없이 생성
        return genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

# 8. 대화 출력
st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 분석 서비스</div>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. 입력 처리
if prompt := st.chat_input("URL 또는 질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("구글 검색과 기사 분석을 동시에 진행 중입니다..."):
            try:
                # URL 감지 및 본문 추출
                article_text = ""
                if "http" in prompt:
                    words = prompt.split()
                    for word in words:
                        if word.startswith("http"):
                            article_text = get_article_text(word)
                            break

                # 모델 생성 (검색 기능 포함)
                try:
                    model = get_model(use_search=True)
                    chat = model.start_chat(history=[])
                except:
                    # 검색 도구에서 에러나면 일반 모델로 전환
                    model = get_model(use_search=False)
                    chat = model.start_chat(history=[])

                # 대화 기록 구성
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat.history.append({"role": role, "parts": [msg["content"]]})

                # 최종 입력 구성
                if article_text:
                    final_input = f"다음 기사 내용을 분석하고, 구글 검색으로 관련 인물 이력과 참고 문헌을 추가해서 리포트를 작성해줘:\n\n{article_text}"
                else:
                    final_input = f"구글 검색을 활용하여 다음 질문에 대해 전문 분석 리포트를 작성해줘: {prompt}"

                # 답변 생성
                response = chat.send_message(final_input)
                answer = response.text

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다. (상세: {e})")

# 10. 푸터
st.markdown("<div style='text-align:center;color:#aaa;font-size:12px;padding-top:50px;'>© 2024 Solid-State Battery Analyst Bot</div>", unsafe_allow_html=True)
