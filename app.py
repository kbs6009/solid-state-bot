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
    
    .title { font-size: 28px; font-weight: 700; color: #000; text-align: center; margin-bottom: 10px; }
    .subtitle { font-size: 15px; color: #666; text-align: center; margin-bottom: 30px; }
    
    /* 민트색 버튼 스타일 */
    .stButton>button { 
        width: 100%; background-color: #37b5a5; color: #fff; border-radius: 5px; 
        padding: 12px; font-size: 16px; font-weight: 700; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2d9387; color: #fff; }
    
    /* 챗봇 말풍선 스타일 */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    
    /* 입력창 테두리 민트색 강조 */
    .stChatInput input:focus { border-color: #37b5a5 !important; }
    
    /* 인증 화면 박스 */
    .auth-box {
        padding: 40px; border-radius: 10px; border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        background-color: #ffffff;
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
    st.markdown("<div style='padding-top: 60px;'></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        # 중앙 로고 이미지 (안정적인 위키미디어 링크)
        st.markdown("<div style='margin-bottom:30px;'><img src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/LG_Energy_Solution_logo.svg/1024px-LG_Energy_Solution_logo.svg.png' width='250'></div>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Solid-State Battery Analyst</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>서비스 이용을 위해 인증이 필요합니다.</div>", unsafe_allow_html=True)
        
        input_password = st.text_input("Password", type="password", placeholder="암호를 입력하세요", label_visibility="collapsed")
        if st.button("접속하기"):
            if input_password == "grsi":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 암호가 올바르지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. 챗봇 화면 로직 (인증 완료 시)
else:
    # 사이드바 설정 (이미지 제거됨)
    with st.sidebar:
        st.markdown("### **수석 애널리스트 챗봇**")
        st.write("전고체전지 기사 URL을 입력하시면 실시간 구글 검색을 통해 전문적인 분석 리포트를 제공합니다.")
        st.markdown("---")
        if st.button("대화 기록 초기화"):
            st.session_state.messages = []
            st.rerun()

    # 메인 챗봇 화면 상단
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 분석 서비스</div>", unsafe_allow_html=True)

    # API 설정
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    except Exception:
        st.error("API Key 설정 오류. Streamlit Secrets를 확인하세요.")
        st.stop()

    # 시스템 프롬프트
    SYSTEM_PROMPT = """당신은 2차전지 및 전고체전지 산업 수석 애널리스트입니다. 
사용자가 URL을 제공하면 반드시 '구글 검색' 기능을 사용하여 해당 페이지의 실제 내용을 읽고 분석하세요.
반드시 한국 대기업식 개조식 요약문(~임, ~함)으로 작성하세요.

[분석 양식]
1. 📝 핵심 요약: 기사의 핵심 내용을 5문장 내외로 요약.
2. 🔑 주요 키워드: 기업명, 연구실, 주요 기술항목 추출.
3. 📈 파급력 분석 (큼 / 중간 / 작음): 기술적 근거를 바탕으로 판별.
4. 💡 애널리스트 인사이트: 시장 판도 변화 및 기술적 기인 요소 분석."""

    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("기사 URL을 입력하거나 질문을 남겨주세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("구글 검색을 통해 기사 원문을 분석 중입니다..."):
                try:
                    # ★ 핵심 수정: Gemini 2.0 모델과 최신 google_search 도구 사용 규격
                    # 최신 SDK에서는 tools=[{"google_search": {}}] 형식을 사용합니다.
                    model = genai.GenerativeModel(
                        model_name="gemini-2.0-flash",
                        tools=[{"google_search": {}}], 
                        system_instruction=SYSTEM_PROMPT
