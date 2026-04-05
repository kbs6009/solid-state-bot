import streamlit as st
import google.generativeai as genai
import requests

# 1. 페이지 설정 및 LG EnSol 스타일 디자인
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석 챗봇", layout="centered")

# 민트색 포인트 컬러: #37b5a5 적용
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #333; }
    
    /* 타이틀 스타일 */
    .title { font-size: 28px; font-weight: 700; color: #000; text-align: center; margin-bottom: 10px; }
    .subtitle { font-size: 15px; color: #666; text-align: center; margin-bottom: 30px; }
    
    /* 민트색 버튼 스타일 */
    .stButton>button { 
        width: 100%; background-color: #37b5a5; color: #fff; border-radius: 5px; 
        padding: 12px; font-size: 16px; font-weight: 700; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2d9387; color: #fff; }
    
    /* 인증 화면 박스 */
    .auth-box {
        padding: 40px; border-radius: 10px; border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# URL 내용을 읽어오는 함수 (Jina Reader 사용)
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

# 3. 인증 로직 (첫 화면 중앙 배치)
if not st.session_state.authenticated:
    st.markdown("<div style='padding-top: 80px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        # LG에너지솔루션 로고
        st.markdown("<div style='margin-bottom:30px;'><img src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/LG_Energy_Solution_logo.svg/1024px-LG_Energy_Solution_logo.svg.png' width='220'></div>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Solid-State Battery Analyst</div>", unsafe_allow_html=True)
        
        pw = st.text_input("Password", type="password", placeholder="암호를 입력하세요", label_visibility="collapsed")
        if st.button("접속하기"):
            if pw == "grsi":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 올바르지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. 사이드바 (이미지 없이 깔끔하게)
with st.sidebar:
    st.markdown("### **수석 애널리스트 챗봇**")
    st.write("기사 URL을 입력하시면 전문적인 분석 리포트를 제공합니다.")
    st.markdown("---")
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

[분석 양식]
1. 핵심 요약 (5줄)
2. 주요 키워드
3. 파급력 분석 (큼/중간/작음)
4. 애널리스트 인사이트
"""

# 7. 모델 생성 (사용자님 설정 유지)
# gemini-2.5-flash는 아직 공식 출시 전이므로, 안정적인 gemini-1.5-flash를 추천하지만 
# 사용자님 환경에서 작동한다면 그대로 두셔도 됩니다. 여기서는 1.5-flash로 적어두겠습니다.
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# 8. 기존 대화 출력
st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 분석 서비스</div>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. 입력 처리 및 URL 읽기 기능
if prompt := st.chat_input("URL 또는 질문을 입력하세요"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("기사 내용을 읽어와서 분석 중입니다..."):
            try:
                # ✅ URL이 포함되어 있으면 내용을 긁어옴
                article_text = ""
                if "http" in prompt:
                    url = [word for word in prompt.split() if word.startswith("http")][0]
                    article_text = get_article_text(url)

                # 대화 기록(History) 구성
                chat = model.start_chat(history=[])
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat.history.append({"role": role, "parts": [msg["content"]]})

                # 기사 내용이 있으면 기사 내용을 포함해서 질문, 없으면 그냥 질문
                if article_text:
                    final_input = f"다음 기사 내용을 읽고 분석 양식에 맞춰 리포트를 써줘:\n\n{article_text}"
                else:
                    final_input = prompt

                response = chat.send_message(final_input)
                answer = response.text

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"에러 발생: {e}")

# 10. 푸터
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:12px;padding-top:50px;'>© 2024 Solid-State Battery Analyst Bot</div>",
    unsafe_allow_html=True
)
