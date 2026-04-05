import streamlit as st
from google import genai
from google.genai import types
import requests

# 1. 페이지 설정 및 LG EnSol 스타일 디자인 (민트 포인트)
st.set_page_config(page_title="LG EnSol 전고체전지 기술 분석 챗봇", layout="centered")

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

# Jina Reader (URL 본문 추출 보조)
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
        # 중앙 로고 이미지
        st.markdown("<div class='title'>All Solid State Battery Article Analyzer</div>", unsafe_allow_html=True)
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
    # 사이드바 설정
    with st.sidebar:
        st.markdown("### **전고체전지 기사 분석 봇**")
        st.write("전고체전지 기술 관련 기사를 분석합니다.")
        st.markdown("---")
        if st.button("대화 기록 초기화"):
            st.session_state.messages = []
            st.rerun()

    # 메인 챗봇 화면 상단
    st.markdown("<div style='text-align: center; padding-bottom: 20px;'><span style='color:#37b5a5; font-weight:700;'>LG EnSol Style</span> 전고체전지 기술 관련 기사 분석 봇</div>", unsafe_allow_html=True)

    # API 클라이언트 설정
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=MY_API_KEY)
    except Exception:
        st.error("API Key 설정 오류. Streamlit Secrets를 확인하세요.")
        st.stop()

    # 시스템 프롬프트 (사용자 요청 원문 그대로 유지)
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
과제 해결: 1) 황화물 고체전해질(Li2S 등) 가격 하락, 2) 혁신 공정을 통한 연간 GWh급 대량 생산 및 가공비 절감, 3) 저온 성능 확보(최소 0~25도), 4) 낮은 구동 가압(1MPa 이하에서 목표 성능 달성)

[전고체전지 분류 및 분석 규칙] 
전해질 종류(산화물, 황화물, 고분자)를 명확히 구분할 것. (산화물: 고온/소형 위주, 황화물: 이온전도도 높아 가장 유망, 고분자: 기존 공정 활용 가능) 
양극에 액체/겔/젤 고분자 전해질을 일부라도 사용했다면 '반고체전지(Semi-solid)'로 엄격히 구분할 것. 
기업 로드맵에 여러 종류의 전지가 등장하면 제품별 출시 시기를 구분하여 정리할 것.

[분석 양식] 
📝 핵심 요약 
기사의 가장 중요한 사실, 이벤트, 결과를 5문장 내외로 요약. 

🔑 주요 키워드 
핵심 기업명, 연구실(교수명), 주요 기술항목(소재, 전극 기술, 셀 구조/설계 등)을 3~5개 추출. 
기업명이 나온 경우는 해당 기업의 기사, 홈페이지를 검색해 대표 및 기술임원, 기술자와 해당 인물의 이력을 간단히 작성.
(이력 정리는 지어내지 말고 반드시 검색결과에 의존해 작성) 

📈 파급력 분석 (큼 / 중간 / 작음) 
기사에 아래 항목과 관련된 내용이 있을 경우에만 판별 및 근거 서술 (언급이 없으면 해당 항목 생략). 
-[저온 성능] 상온 성능 우수 주장 시 '중간', 0도 이하 성능 강조 시 '큼' 
-[구동 가압] 2MPa 이하는 '중간', 1MPa 이하는 '큼' 
-[안전성] 단순 내열성 우수는 '작음', 네일/파괴 테스트 통과는 '중간', 열전파(Thermal propagation) 완벽 차단은 '큼' 
-[재료비] 고체전해질 가격의 획기적 하락 가능성 제시 시 '큼' 
-[공정비/양산] 27~28년 양산 또는 직접적 생산비용 절감 주장 시 '큼', 28~29년 양산은 '중간', 30년 이후는 '작음' 

검색을 통해서도 정확한 데이터(온도, 압력, 연도, GWh, 출신 학교, 논문 링크 등)를 찾을 수 없다면 절대 지어내지 말고 "확인 불가"로 명시할 것. 
기술문헌 근거는 분석 마지막에 정리하여 작성 

💡 분석가 인사이트
1. 기사가 향후 전고체전지 시장 판도(상용화 시기, 밸류체인 변화, 경쟁 구도 등)에 미칠 영향을 산업적 맥락을 더해 5줄 이내로 분석. 
2. 위에서 찾은 기업, 인물과 전고체전지 연관 기사, 논문, 특허를 검색하고, 파급력이 어떠한 기술에서 기인하였는지를 분석. 
양극재/음극재/전해질/바인더 등 소재기술, 조성 및 전극 공정 등 전극 기술, 셀 구조 및 설계 등 셀 기술로 구분하여 어떤 기술에서 기인하였는지 설명하고 그 근거가 된 문헌 링크를 반드시 기재. 
링크와 내용의 연결은 지어내지말고 실제 검색 결과 바탕으로 그 내에서 정리할 것.

마크다운(Markdown) 형식을 사용하여 가독성을 높일 것. 기사에 없는 사실을 지어내지 말 것(환각 방지).
어조는 전문적이고 객관적일 것. 
★문체: 반드시 한국 대기업식 '개조식 요약문'으로 작성할 것. (예: "~임", "~로 판단됨", "파급력 큼", "고성능 확보" 등 명사형 또는 명사조사로 문장 종결. "~습니다", "~해요" 사용 금지)"""

    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("기사 URL을 입력해 주세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("책임 연구원이 기술 분석 및 웹 검색을 수행 중입니다..."):
                try:
                    # URL 감지 및 본문 추출
                    article_text = ""
                    if "http" in prompt:
                        words = prompt.split()
                        for word in words:
                            if word.startswith("http"):
                                article_text = get_article_text(word)
                                break
                    
                    # 구글 검색 도구 설정
                    google_search_tool = types.Tool(google_search=types.GoogleSearch())
                    
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=[google_search_tool],
                        temperature=0.2
                    )
                    
                    # 대화 기록 변환
                    history_contents = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        history_contents.append(
                            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                        )
                    
                    # 챗봇 생성 (gemini-2.5-flash 사용)
                    chat = client.chats.create(
                        model="gemini-2.5-flash",
                        config=config,
                        history=history_contents
                    )
                    
                    final_input = f"다음 기사 내용을 분석하고 구글 검색을 통해 심층 기술 분석을 수행해줘:\n\n{article_text if article_text else prompt}"
                    
                    response = chat.send_message(final_input)
                    full_response = response.text
                    
                    # 1. AI의 분석 결과 출력
                    st.markdown(full_response)

                    # 2. ★ 클릭 가능한 참고 문헌(출처) 링크 자동 생성
                    # Google Search Grounding Metadata를 사용하여 실제 검색에 쓰인 출처를 추출합니다.
                    try:
                        if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.search_entry_point:
                            st.markdown("---")
                            st.markdown("#### 🔗 검색 데이터 출처 (Verified Sources)")
                            # 구글에서 제공하는 공식 "Search Google" 칩/버튼 렌더링
                            st.html(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)
                            
                        # 개별 링크 목록 추출 (구조화된 링크가 있을 경우)
                        if response.candidates[0].grounding_metadata.grounding_chunks:
                            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                                if chunk.web:
                                    st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")
                    except:
                        pass # 출처 데이터가 없는 경우 조용히 넘어감

                    # 메시지 저장
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")

# 하단 푸터
st.markdown("<div style='text-align: center; color: #bbb; font-size: 11px; padding-top: 50px;'>© 2026 Solid-State Battery Technical Analysis Chatbot. All rights reserved.</div>", unsafe_allow_html=True)
