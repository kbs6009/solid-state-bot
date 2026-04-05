import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="LG EnSol Style - 전고체전지 분석", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #333; }
    .title { font-size: 36px; font-weight: 700; color: #000; text-align: center; margin-bottom: 10px; letter-spacing: -1px; }
    .subtitle { font-size: 16px; color: #666; text-align: center; margin-bottom: 50px; }
    .required { color: #e6007e; margin-left: 4px; }
    .stButton>button { width: 100%; background-color: #000; color: #fff; border-radius: 0px; padding: 15px; font-size: 16px; font-weight: 700; border: none; margin-top: 20px; }
    .stButton>button:hover { background-color: #333; color: #fff; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #eee; }
    .result-box { background-color: #fdfdfd; border: 1px solid #ddd; padding: 25px; margin-top: 30px; border-radius: 5px; line-height: 1.8; }
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
    st.markdown("<div class='title'>전고체전지 기사 분석 봇</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>기사 URL을 입력하시면 전문 애널리스트의 분석 리포트를 제공합니다.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # [보안 적용] 스트림릿 Secrets에서 API 키를 가져옵니다.
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Streamlit Cloud의 Secrets 설정에서 GEMINI_API_KEY를 찾을 수 없습니다.")
            st.stop()
        
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    except Exception as e:
        st.error(f"설정 오류: {e}")
        st.stop()

    # 시스템 프롬프트 설정
    SYSTEM_PROMPT = "당신은 2차전지 및 전고체전지 산업 수석 애널리스트입니다. 반드시 한국 대기업식 개조식 요약문(~임, ~함)으로 작성하세요. 1. 핵심 요약(5문장), 2. 주요 키워드(기업/기술), 3. 파급력 분석(큼/중간/작음), 4. 애널리스트 인사이트(시장 판도 변화) 순서로 분석하세요."

    # 입력 폼
    st.markdown("<div>기사 URL <span class='required'>*</span></div>", unsafe_allow_html=True)
    user_input = st.text_input("URL을 입력해 주세요.", label_visibility="collapsed", placeholder="https://news.naver.com/...")

    if st.button("리포트 생성하기"):
        if not user_input:
            st.error("분석할 URL을 입력해 주세요.")
        else:
            with st.spinner("데이터를 정밀 분석 중입니다. 잠시만 기다려 주십시오..."):
                try:
                    # 모델 이름을 정확하게 지정 (gemini-1.5-flash)
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    # 답변 생성
                    response = model.generate_content(user_input)
                    
                    if response.text:
                        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                        st.markdown("### 📊 전고체전지 기사 분석 리포트")
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어 있습니다. URL을 다시 확인해 주세요.")
                        
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
                    st.info("라이브러리 버전이나 모델 이름 설정을 다시 확인 중입니다.")

else:
    st.markdown("<div class='title' style='margin-top:100px;'>Service Access</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>본 서비스는 승인된 사용자만 이용 가능합니다.<br>사이드바에서 암호를 입력해 주십시오.</div>", unsafe_allow_html=True)
    if password and password != "grsi":
        st.sidebar.error("❌ 암호가 일치하지 않습니다.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #999; font-size: 12px;'>© 2024 Solid-State Battery Analy
