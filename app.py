import streamlit as st
import google.generativeai as genai
import requests

# 1. 페이지 설정 및 LG EnSol 스타일 디자인 (민트 포인트)
st.set_page_config(page_title="LG EnSol Style - 전고체전지 기술 분석 챗봇", layout="centered")

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

# Jina Reader (URL 본문 추출 보조 도구)
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

# 3. 인증 로직 (첫 화면 중앙 로고 배치)
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
    # 사이드바 설정 (이미지 제거)
    with st.sidebar:
        st.markdown("### **책임 연구원 챗봇**")
        st.write("전고체전지 기술 분석을 수행합니다.")
        st.markdown("---")
        if st.button("대화 기록 초기화"):
            st.session_state.messages = []
            st.rerun()

    # 메인 챗봇 화면 상단
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 기술 분석 서비스</div>", unsafe_allow_html=True)

    # API 설정
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    except Exception:
        st.error("API Key 설정 오류. Streamlit Secrets를 확인하세요.")
        st.stop()

    # 요청하신 상세 시스템 프롬프트
    SYSTEM_PROMPT = """You have access to Google Search. To use it, you MUST first output your internal reasoning (Thought) about why the search is necessary, and then perform the function call.
IMPORTANT: Before calling any tool, you must first output a detailed 'Thought' section. Never provide a function call without a preceding thought.

당신은 전고체전지(All-Solid-State Battery) 기사에 대해 심도있는 기술적 분석을 수행하는 전지 제조 업체의 책임 연구원입니다.
사용자가 전고체전지 관련 URL을 입력하면 아래의 [평가 프레임워크]와 [분석 양식]에 맞춰 정량적이고 통찰력 있는 기술 분석을 제공해야 합니다.

[검색 및 데이터 검증 규칙] 
URL이 아닌경우 대화의 흐름에 맞게 전문적인 대답을 하십시오. 
URL이 제공될 경우: 임의로 내용을 추측하지 말고, 반드시 '웹 브라우징 도구'를 사용해 해당 URL의 실제 텍스트를 추출하여 분석할 것. 

팩트 체크: 검색으로 알 수 있는 정보에 한해 최대한 정량적으로 정확한 값(온도, 압력, 연도, GWh 등)을 사용할 것. 모르는 것은 "확인 불가"로 답할 것. 
출처 표기: 분석에 사용된 기술적 근거와 데이터는 반드시 리포트 하단에 참고한 웹사이트 링크(출처)를 표기할 것.

[애널리스트의 평가 프레임워크] 
당신은 전고체전지 상용화를 위해 다음 조건이 입증되어야 한다고 판단합니다. 기사 분석 시 이 기준을 적용하세요. 
장점 입증: 1) 높은 에너지밀도(팩 공간활용률), 2) 10분 이내 급속충전(10~80%), 3) LFP 이상의 열폭주 안전성 
과제 해결: 1) 황화물 고체전해질(Li2S 등) 가격 하락, 2) 혁신 공정을 통한 연간 GWh급 대량 생산 및 가공비 절감, 3) 저온 성능 확보(최
