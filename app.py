import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 디자인 (LG 에너지솔루션 스타일 CSS)
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 화이트 */
    .main {
        background-color: #ffffff;
    }
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333;
    }
    /* 타이틀 스타일 */
    .title {
        font-size: 36px;
        font-weight: 700;
        color: #000;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    .subtitle {
        font-size: 16px;
        color: #666;
        text-align: center;
        margin-bottom: 50px;
    }
    /* 입력창 라벨 스타일 */
    .stTextInput label, .stTextArea label {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #333 !important;
    }
    /* 필수 표시(*) 스타일 */
    .required {
        color: #e6007e;
        margin-left: 4px;
    }
    /* 버튼 스타일 (LG EnSol 블랙 버튼 스타일) */
    .stButton>button {
        width: 100%;
        background-color: #000;
        color: #fff;
        border-radius: 0px;
        padding: 15px;
        font-size: 16px;
        font-weight: 700;
        border: none;
        margin-top: 20px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #333;
        color: #fff;
    }
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #eee;
    }
    /* 결과창 박스 스타일 */
    .result-box {
        background-color: #fdfdfd;
        border: 1px solid #ddd;
        padding: 25px;
        margin-top: 30px;
        border-radius: 5px;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바 - 암호 입력창
with st.sidebar:
    st.markdown("<div style='padding: 20px 0; text-align:center;'><img src='https://www.lgensol.com/assets/img/common/logo.png' width='150'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.header("🔐 접속 인증")
    password = st.text_input("암호를 입력하세요", type="password")

# 3. 메인 화면 로직
if password == "grsi":
    # 타이틀 영역
    st.markdown("<div class='title'>전고체전지 산업 분석 서비스</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>기사 URL을 입력하시면 전문 애널리스트의 분석 리포트를 제공합니다.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # [보안 적용] 스트림릿 Secrets에서 API 키를 안전하게 가져옵니다.
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    except Exception:
        st.error("API Key 설정이 완료되지 않았습니다. Streamlit Cloud의 Secrets 설정을 확인해주세요.")
        st.stop()

    # 시스템 프롬프트
    SYSTEM_PROMPT = """
당신은 2차전지 및 전고체전지(All-Solid-State Battery) 산업을 심도 있게 분석하는 수석 애널리스트입니다.
반드시 한국 대기업식 '개조식 요약문'으로 작성할 것. (~임, ~함, ~로 판단됨 등)

[분석 양식]
1. 📝 핵심 요약: 기사의 핵심 내용을 5문장 내외로 요약.
2. 🔑 주요 키워드: 기업명,
