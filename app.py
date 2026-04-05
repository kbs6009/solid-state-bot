import streamlit as st
import google.generativeai as genai

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="전고체전지 분석기", layout="wide")

# 2. 사이드바 - 암호 입력창
with st.sidebar:
    st.header("🔐 접속 인증")
    password = st.text_input("암호를 입력하세요", type="password")
    st.info("인증이 완료되면 분석 기능이 활성화됩니다.")

# 3. 암호 확인 (grsi)
if password == "grsi":
    st.success("✅ 인증되었습니다. 수석 애널리스트 모드가 활성화되었습니다.")
    
    # --- 여기서부터 본문 내용 ---
    st.title("🔋 전고체전지 전문 분석 챗봇")
    st.write("기사 URL을 입력하면 전문적인 산업 분석 리포트를 생성합니다.")

    # [보안 주의] API 키를 코드에 직접 넣습니다.
    # 본인의 실제 API 키를 아래 따옴표 안에 붙여넣으세요.
    MY_API_KEY = "YOUR_GOOGLE_API_KEY_HERE" 
    genai.configure(api_key=MY_API_KEY)

    # 확정된 시스템 프롬프트 (수석 애널리스트 페르소나)
    SYSTEM_PROMPT = """
당신은 2차전지 및 전고체전지(All-Solid-State Battery) 산업을 심도 있게 분석하는 수석 애널리스트입니다.
사용자가 전고체전지 관련 URL을 입력하면 아래의 [평가 프레임워크]와 [분석 양식]에 맞춰 정량적이고 통찰력 있는 분석을 제공해야 합니다.

[검색 및 데이터 검증 규칙]
URL이 아닌경우 대화의 흐름에 맞게 전문적인 대답을 하십시오.
1. URL이 제공될 경우: 임의로 내용을 추측하지 말고, 제공된 내용을 바탕으로 분석할 것.
2. 팩트 체크: 최대한 정량적으로 정확한 값(온도, 압력, 연도, GWh 등)을 사용할 것. 모르는 것은 "확인 불가"로 답할 것.

[애널리스트의 평가 프레임워크]
당신은 전고체전지 상용화를 위해 다음 조건이 입증되어야 한다고 판단합니다.
- 장점 입증: 1) 높은 에너지밀도, 2) 10분 이내 급속충전, 3) 열폭주 안전성
- 과제 해결: 1) 황화물 고체전해질 가격 하락, 2) 혁신 공정을 통한 대량 생산, 3) 저온 성능 확보, 4) 낮은 구동 가압(1MPa 이하)

[분석 양식]
1. 📝 핵심 요약: 기사의 핵심 내용을 5문장 내외로 요약.
2. 🔑 주요 키워드: 기업명, 연구실, 주요 기술항목 추출 및 인물 이력 요약(아는 범위 내).
3. 📈 파급력 분석 (큼 / 중간 / 작음): 저온 성능, 구동 가압, 안전성, 재료비, 공정비/양산성 기준.
4. 💡 애널리스트 인사이트: 시장 판도 변화 및 기술적 기인 요소 분석(양극재/음극재/전해질/공정 등 구분).

★문체: 반드시 한국 대기업식 '개조식 요약문'으로 작성할 것. (~임, ~함, ~로 판단됨 등)
    """

    # 사용자 입력창
    user_input = st.text_area("분석할 기사 URL을 입력하세요:", placeholder="https://news.naver.com/...")

    if st.button("🚀 리포트 생성 시작"):
        if not user_input:
            st.warning("분석할 URL을 입력해주세요.")
        else:
            with st.spinner("애널리스트가 데이터를 정밀 분석 중입니다..."):
                try:
                    # Gemini 모델 설정
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    # 답변 생성
                    response = model.generate_content(user_input)
                    
                    # 결과 출력
                    st.markdown("---")
                    st.markdown("### 📊 전고체전지 산업 분석 리포트")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

else:
    # 암호가 틀리거나 입력되지 않았을 때
    st.title("🔋 전고체전지 전문 분석 챗봇")
    st.warning("사이드바에 올바른 암호를 입력해야 서비스를 이용할 수 있습니다.")
    if password and password != "grsi":
        st.error("❌ 암호가 틀렸습니다. 다시 확인해주세요.")
