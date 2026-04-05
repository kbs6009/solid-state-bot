import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 디자인 (LG EnSol 스타일 + 민트 포인트)
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석 챗봇", layout="centered")

# 민트색 포인트 컬러: #37b5a5
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #333; }
    
    /* 타이틀 및 텍스트 스타일 */
    .title { font-size: 32px; font-weight: 700; color: #000; text-align: center; margin-bottom: 10px; }
    .subtitle { font-size: 16px; color: #666; text-align: center; margin-bottom: 30px; }
    
    /* 민트색 버튼 스타일 */
    .stButton>button { 
        width: 100%; background-color: #37b5a5; color: #fff; border-radius: 5px; 
        padding: 12px; font-size: 16px; font-weight: 700; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2d9387; color: #fff; }
    
    /* 챗봇 말풍선 수정 */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    
    /* 입력창 테두리 민트색 강조 */
    .stChatInput input:focus { border-color: #37b5a5 !important; }
    
    /* 인증 화면 박스 */
    .auth-box {
        padding: 40px; border-radius: 10px; border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 상태 초기화 (인증 및 대화 기록)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 인증 로직 (첫 화면)
if not st.session_state.authenticated:
    st.markdown("<div style='padding-top: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Solid-State Battery Analyst</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>서비스 이용을 위해 인증이 필요합니다.</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        input_password = st.text_input("Password", type="password", placeholder="암호를 입력하세요")
        if st.button("접속하기"):
            if input_password == "grsi":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 암호가 올바르지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. 챗봇 화면 로직 (인증 완료 시)
else:
    # 사이드바 설정
    with st.sidebar:
        st.markdown("<div style='text-align:center;'><img src='https://www.lgensol.com/assets/img/common/logo.png' width='130'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### **수석 애널리스트 챗봇**")
        st.write("전고체전지 기사 URL을 입력하시면 전문적인 분석 리포트를 제공합니다.")
        if st.button("대화 기록 초기화"):
            st.session_state.messages = []
            st.rerun()

    # 메인 챗봇 화면 타이틀
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 분석 서비스</div>", unsafe_allow_html=True)

    # API 설정
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    except Exception:
        st.error("API Key 설정 오류. Streamlit Secrets를 확인하세요.")
        st.stop()

    # 시스템 프롬프트
    SYSTEM_PROMPT = "당신은 2차전지 및 전고체전지 산업 수석 애널리스트입니다. 반드시 한국 대기업식 개조식 요약문(~임, ~함)으로 작성하세요. 1. 핵심 요약(5문장), 2. 주요 키워드(기업/기술), 3. 파급력 분석(큼/중간/작음), 4. 애널리스트 인사이트(시장 판도 변화) 순서로 분석하세요."

    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("기사 URL을 입력하거나 질문을 남겨주세요."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("애널리스트가 분석 중입니다..."):
                try:
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    response = model.generate_content(prompt)
                    full_response = response.text
                    st.markdown(full_response)
                    # AI 메시지 저장
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# 하단 푸터
st.markdown("<div style='text-align: center; color: #bbb; font-size: 11px; padding-top: 50px;'>© 2024 Solid-State Battery Analysis Chatbot. All rights reserved.</div>", unsafe_allow_html=True)
