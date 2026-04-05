import streamlit as st
import google.generativeai as genai

# 1. 웹페이지 설정
st.set_page_config(page_title="전고체전지 분석기", layout="wide")
st.title("🔋 전고체전지 전문 분석 챗봇")

# 2. 사이드바 설정 (API 키 입력)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Google API Key를 입력하세요", type="password")

# 3. 확정된 시스템 프롬프트 (여기에 아까 만든 프롬프트를 넣었습니다)
SYSTEM_PROMPT = """
당신은 2차전지 및 전고체전지(All-Solid-State Battery) 산업을 심도 있게 분석하는 수석 애널리스트입니다.
사용자가 전고체전지 관련 URL을 입력하면 아래의 [평가 프레임워크]와 [분석 양식]에 맞춰 정량적이고 통찰력 있는 분석을 제공해야 합니다.

(중략 - 아까 확정하신 긴 프롬프트 내용을 여기에 그대로 넣으시면 됩니다)
"""

# 4. 분석 로직
user_input = st.text_input("분석할 기사 URL을 입력하세요:", placeholder="https://...")

if st.button("분석 시작"):
    if not api_key:
        st.error("API Key를 입력해주세요!")
    elif not user_input:
        st.warning("URL을 입력해주세요!")
    else:
        with st.spinner("애널리스트가 분석 중입니다..."):
            try:
                # Gemini 설정
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_PROMPT # 시스템 프롬프트 주입
                )
                
                # 답변 생성
                response = model.generate_content(user_input)
                
                st.markdown("### 📊 분석 결과")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
