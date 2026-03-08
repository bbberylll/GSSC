import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import os
import time
from streamlit.runtime.scriptrunner import get_script_run_ctx

# 1. 페이지 설정
st.set_page_config(page_title="CultureFIT - AI Scenario Guardrail", layout="wide")

# --- 설정값 ---
MAIN_COLOR = "#6c86ff"  # CultureFIT 브랜드 컬러
POINT_COLOR = "#007bff" # 최종 결론 파란색

# --- 누적 접속자 로직 ---
COUNTER_FILE = "total_counter.txt"
if not os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "w") as f: f.write("78")

ctx = get_script_run_ctx()
if ctx and f"{ctx.session_id}.visited" not in st.session_state:
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r+") as f:
            content = f.read().strip()
            count = int(content) if content else 78
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
    st.session_state[f"{ctx.session_id}.visited"] = True

def get_total_users():
    with open(COUNTER_FILE, "r") as f: return f.read()

# --- CSS 스타일 ---
st.markdown(f"""
    <style>
    /* Google Material Symbols 라이브러리 호출 */
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    .stApp {{ background-color: #ffffff; }}

    /* 상단 헤더 */
    .main-header {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 30px; background-color: white; border-bottom: 1px solid #eee; margin-bottom: 30px;
    }}
    .logo {{ color: {MAIN_COLOR}; font-size: 32px; font-weight: bold; letter-spacing: -1.5px; }}

    /* 아이콘 스타일링 */
    .material-symbols-outlined {{
        font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
        cursor: pointer;
        transition: 0.2s;
        font-size: 26px;
        color: #666;
        display: inline-block;
    }}
    .material-symbols-outlined:hover {{
        color: {MAIN_COLOR};
        font-variation-settings: 'FILL' 1;
    }}
    .header-icons {{ display: flex; gap: 20px; align-items: center; }}

    /* 대시보드 메트릭 */
    .metric-container {{ background-color: #f8faff; padding: 18px; border-radius: 12px; text-align: center; border: 1px solid #eef2ff; }}
    .metric-val {{ font-size: 26px; font-weight: bold; color: {MAIN_COLOR}; display: block; }}
    .metric-label {{ font-size: 14px; color: #888; font-weight: 500; }}

    /* 버튼 커스터마이징 */
    div.stButton > button {{
        background-color: {MAIN_COLOR}; color: white; border-radius: 8px; border: none;
        padding: 10px 20px; font-weight: 600; width: 100%; transition: 0.3s;
    }}
    div.stButton > button:hover {{ background-color: #556edb; border: none !important; color: white !important; }}

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {{ background-color: #fcfcfc; border-right: 1px solid #f0f0f0; }}
    .history-item {{
        display: flex; align-items: center; gap: 8px;
        padding: 10px; border-radius: 8px; font-size: 14px; color: #555;
        transition: 0.2s; cursor: pointer;
    }}
    .history-item:hover {{ background-color: #f0f4ff; color: {MAIN_COLOR}; }}

    /* 스크립트 박스 및 하이라이트 */
    .script-box {{
        font-family: 'Courier New', Courier, monospace; border: 1px solid #eee; padding: 25px;
        border-radius: 12px; height: 550px; overflow-y: auto; line-height: 1.9; font-size: 15px;
        background-color: #fafafa; white-space: pre-wrap;
    }}
    .highlight-red {{ color: #ff4b4b; font-weight: bold; background-color: #fff0f0; padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #ff4b4b; }}
    .highlight-blue {{ color: {MAIN_COLOR}; font-weight: bold; background-color: #eef2ff; padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid {MAIN_COLOR}; }}

    /* 텍스트 에어리어 폰트 */
    .stTextArea textarea {{ font-family: 'Courier New', monospace !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 1. 상단 헤더 (아이콘 교체) ---
st.markdown(f"""
    <div class="main-header">
        <div style="width: 150px;"></div>
        <div class="logo">CultureFIT</div>
        <div class="header-icons">
            <span class="material-symbols-outlined" title="Share">share</span>
            <span class="material-symbols-outlined" title="Settings">settings</span>
            <span class="material-symbols-outlined" title="Account">account_circle</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 사이드바 (프로젝트 관리 및 아이콘 추가) ---
with st.sidebar:
    st.markdown("### Projects")
    if st.button("+ New Project"):
        st.session_state.analyzed = False
        st.session_state.is_fixed = False
        st.rerun()

    st.write("")
    st.caption("Recent Analysis")
    history_list = ["조선 초기 배경 역사 드라마 고증 분석", "한국 타겟 다큐멘터리 번역 점검", "베트남 배경의 영화 문화 맥락 점검"]
    for item in history_list:
        st.markdown(f'<div class="history-item"><span class="material-symbols-outlined" style="font-size: 18px;">description</span>{item}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 40vh;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("⚙️ System Settings"):
        st.toast("설정 메뉴 준비 중")

# --- 3. 상태 관리 ---
if "analyzed" not in st.session_state: st.session_state.analyzed = False
if "is_fixed" not in st.session_state: st.session_state.is_fixed = False
if "script_content" not in st.session_state:
    ##st.session_state.script_content = """S# 12. 기방 내실 (밤)\n\n충녕, 서양 사제 앞에 앉아 있다. \n서양 사제의 앞에는 기름진 월병과 피단이 놓인 상이 차려져 있다.\n\n충녕: (잔을 채우며) 먼 길 오느라 고생하셨소. \n서양 사제: (서툰 조선말로) 건국 대왕께서 악령의 도움을 받으셨다는 이야기는 익히 들었습니다.\n충녕: (무겁게 끄덕이며) 그것이 우리 가문의 지워지지 않는 비화지요.\n\n이때, 문이 열리며 무화가 들어온다. \n그녀는 화려한 중국풍 의상을 입고 묘한 미소를 지으며 춤을 추기 시작한다."""
    st.session_state.script_content = """1932년 4월 29일, 상하이 훙커우 공원. 일본군의 천장절 기념식이 한창이었다. 군복 차림의 사내들이 단상을 가득 메운 가운데, 한 조선 청년이 군중 속에 조용히 섞여 들었다.\n\n청년의 이름은 윤봉길. 그의 손에는 도시락 모양의 폭탄이 들려 있었다. 숨을 고른 그는 단상을 향해 힘껏 던졌다. 폭발과 함께 단상이 무너지고, 일본군 장성들이 쓰러졌다. 거사는 성공이었다. 그는 그 자리에서 체포됐지만, 얼굴에는 두려움 대신 결연함이 남아 있었다."""


    
# --- 4. 메인 대시보드 지표 (이모티콘 -> 아이콘 교체) ---
total_users = get_total_users()
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'''<div class="metric-container">
        <span class="material-symbols-outlined" style="color:{MAIN_COLOR}">trending_up</span>
        <span class="metric-label">누적 접속자 수</span><span class="metric-val">{total_users}명</span>
    </div>''', unsafe_allow_html=True)
with m2:
    st.markdown(f'''<div class="metric-container">
        <span class="material-symbols-outlined" style="color:{MAIN_COLOR}">shield_with_heart</span>
        <span class="metric-label">가드레일 작동</span><span class="metric-val">41건</span>
    </div>''', unsafe_allow_html=True)
with m3:
    st.markdown(f'''<div class="metric-container">
        <span class="material-symbols-outlined" style="color:{MAIN_COLOR}">verified</span>
        <span class="metric-label">데이터 신뢰도</span><span class="metric-val">91.8%</span>
    </div>''', unsafe_allow_html=True)

st.write("")

# --- 5. 메인 레이아웃 ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown(f'##### <span class="material-symbols-outlined" style="vertical-align: middle; font-size:20px;">edit_note</span> Script Editor', unsafe_allow_html=True)
    
    # 1. AI 엔진 선택
    st.selectbox("Analysis Engine", ["gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-3-pro-preview",
        "gpt-5.2", "gpt-5.1", "claude-sonnet-4-5", "qwen3-coder", "qwen3-tput", "gpt-oss"], label_visibility="collapsed")
    
    # 2. 시대 배경 입력 칸
    era_input = st.text_input("분석 대상 시대 및 지역 입력", 
        placeholder="예: 조선, 한양 / 현대, 서울 / 고려, 개경", 
        help="검증하고자 하는 작품의 핵심 배경 키워드를 입력해주세요.")

    # --- 가드레일 작동 알림 영역 ---
    if not st.session_state.analyzed and era_input != "":
        # '조선'도 없고 '일제'도 없을 때만 가드레일 작동
        if "조선" not in era_input and "일제" not in era_input:
            st.error(f"⚠️ 가드레일 작동: '{era_input}' 배경은 현재 온톨로지 검증 범위를 벗어납니다.")
            st.info("💡 CultureFIT은 현재 **'조선시대'** 및 **'일제강점기'** 역사 데이터에 특화되어 있습니다. 해당 시나리오는 아직 가드레일이 작동할 수 없습니다.")

    if not st.session_state.analyzed:
        st.session_state.script_content = st.text_area("Script Input", value=st.session_state.script_content, height=550, label_visibility="collapsed")

        if st.button("🔎 고증 정합성 검사 시작"):
            # 버튼 클릭 시에도 동일하게 체크
            if "조선" in era_input or "일제" in era_input:
                st.session_state.analyzed = True
                st.rerun()
            elif era_input == "":
                st.warning("작품의 시대 배경을 입력해주세요.")
    
    else:
        # 분석 후: 결과 표시
        text = st.session_state.script_content
        if st.session_state.is_fixed:
            # 두 시나리오의 교정 키워드 모두 포함
            for kw in ["다식과 송기떡", "명나라 관리", "백성들의 염원", "전통 한복", "물통형 모양 폭탄"]:
                text = text.replace(kw, f'<span class="highlight-blue">{kw}</span>')
            st.info("신뢰할 수 있는 사료를 바탕으로 교정이 완료되었습니다.")
        else:
            # 두 시나리오의 위반 키워드 모두 포함
            for kw in ["월병", "서양 사제", "악령의 도움", "중국풍 의상", "도시락 모양의 폭탄"]:
                text = text.replace(kw, f'<span class="highlight-red">{kw}</span>')
            st.error("주의: 역사적 사실과 불일치하는 설정이 감지되었습니다.")

        st.markdown(f'<div class="script-box">{text}</div>', unsafe_allow_html=True)
        
        if st.button("↺ 원본 대본 수정"):
            st.session_state.analyzed = False
            st.rerun()

with right_col:
    st.markdown(f'##### <span class="material-symbols-outlined" style="vertical-align: middle; font-size:20px;">analytics</span> Investigation Report', unsafe_allow_html=True)
    if not st.session_state.analyzed:
        st.info("시나리오 분석을 시작하면 고증 데이터 리포트가 생성됩니다.")
    else:
        if not st.session_state.is_fixed:
            if st.button("✨ 일괄 고증 교정 적용"):
                # 모든 시나리오의 교정 로직 통합
                st.session_state.script_content = st.session_state.script_content.replace("월병", "다식과 송기떡").replace("서양 사제", "명나라 관리").replace("악령의 도움", "백성들의 염원").replace("중국풍 의상", "전통 한복").replace("도시락 모양의 폭탄", "물통형 모양 폭탄")
                st.session_state.is_fixed = True
                st.rerun()

            # --- 대본 내용에 따라 리스트 생성 ---
            issues = []
            if "도시락" in st.session_state.script_content:
                issues.append({"target": "도시락 모양의 폭탄", "reason": "1932년 5월 25일자 상하이 군법회의 판결문에 따르면 실제 투척물은 물통 폭탄임.", "type": "소품"})
            if "월병" in st.session_state.script_content:
                issues.append({"target": "서양 사제", "reason": "15세기 조선에 가톨릭 사제 입국 기록 부재.", "type": "인물"})
                issues.append({"target": "월병", "reason": "중국식 병과로 조선 왕실 의궤에 등장하지 않음.", "type": "소품"})
                # ... 필요한 만큼 추가 가능

            for idx, iss in enumerate(issues):
                with st.expander(f"⚠️ {iss['type']}: [{iss['target']}]"):
                    st.write(f"**분석:** {iss['reason']}")
                    if st.button("지식 경로 추적", key=f"g_{idx}"): st.session_state.selected_issue = iss['target']
        else:
            st.success("검수 완료: 모든 설정이 객관적 사료에 부합합니다.")
            st.write("**고증 로그:**")
            st.markdown("- 인물: 서양 사제 → **명나라 관리**\n- 소품: 월병 → **다식과 송기떡**\n- 서사: 악령의 도움 → **백성들의 염원**\n- 의상: 중국풍 의상 → **전통 한복**")

        # --- 지식 그래프 영역 (변경 없음) ---
        if st.session_state.get("selected_issue"):
            st.write("---")
            # 🌐 대신 아이콘 사용
            st.markdown(f'''
        <h4 style="display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: {MAIN_COLOR};">hub</span>
            <span>"{st.session_state.selected_issue}" 지식 온톨로지 </span>
        </h4>
    ''', unsafe_allow_html=True)

            issue_data = {
                "도시락 모양의 폭탄": {
                    "nodes": [
                        Node(id="Fact", label="실제 투척: 물통 폭탄", size=25, color=POINT_COLOR),
                        Node(id="Evidence", label="상하이 군법회의 판결문(1932)", size=20, color="#4CAF50"),
                        Node(id="Reserve", label="도시락 폭탄: 자결용", size=20, color="#ff4b4b"),
                        Node(id="Source", label="매헌윤봉길의사기념관", size=15, color="#9467bd")
                    ],
                    "edges": [
                        Edge(source="Fact", target="Evidence", label="기록 증명"),
                        Edge(source="Fact", target="Reserve", label="용도 구분")
                    ]
                },
                "서양 사제": {
                    "nodes": [
                        Node(id="Era", label="조선 15세기", size=25, color=MAIN_COLOR),
                        Node(id="Issue", label="서양 사제 설정", size=25, color="#ff4b4b"),
                        Node(id="Fact", label="가톨릭 전래(18세기)", size=20, color="#4CAF50"),
                        Node(id="Ref", label="조선왕조실록 사료", size=15, color="#9467bd"),
                        Node(id="Conclusion", label="역사적 시차 발생", size=20, color=POINT_COLOR)
                    ],
                    "edges": [
                        Edge(source="Era", target="Issue", label="배경 불일치"),
                        Edge(source="Issue", target="Fact", label="300년 시차"),
                        Edge(source="Fact", target="Ref", label="문헌 증명"),
                        Edge(source="Issue", target="Conclusion", label="검증 결과")
                    ]
                },
                "월병": {
                    "nodes": [
                        Node(id="Era", label="조선 왕실 식문화", size=25, color=MAIN_COLOR),
                        Node(id="Issue", label="중국식 소품(월병)", size=25, color="#ff4b4b"),
                        Node(id="Fact", label="전통 병과(다식)", size=20, color="#4CAF50"),
                        Node(id="Source", label="국조오례의/의궤", size=15, color="#9467bd"),
                        Node(id="Result", label="문화적 정체성 오기", size=20, color=POINT_COLOR)
                    ],
                    "edges": [
                        Edge(source="Era", target="Issue", label="복식 기준 위반"),
                        Edge(source="Era", target="Fact", label="정석 배치"),
                        Edge(source="Fact", target="Source", label="기록물 근거"),
                        Edge(source="Issue", target="Result", label="객관적 판정")
                    ]
                },
                "악령의 도움": {
                    "nodes": [
                        Node(id="Origin", label="조선 건국 서사", size=25, color=MAIN_COLOR),
                        Node(id="Issue", label="비현실적 악령 조력", size=25, color="#ff4b4b"),
                        Node(id="Fact", label="유교적 민본주의", size=20, color="#4CAF50"),
                        Node(id="History", label="용비어천가/실록", size=15, color="#9467bd"),
                        Node(id="Critical", label="국가 정통성 왜곡", size=20, color=POINT_COLOR)
                    ],
                    "edges": [
                        Edge(source="Origin", target="Issue", label="서사 왜곡"),
                        Edge(source="Origin", target="Fact", label="역사적 정석"),
                        Edge(source="Fact", target="History", label="사료 증명"),
                        Edge(source="Issue", target="Critical", label="정합성 확인")
                    ]
                },
                "중국풍 의상": {
                    "nodes": [
                        Node(id="Job", label="조선 무녀 복식", size=25, color=MAIN_COLOR),
                        Node(id="Issue", label="타국 양식(중국풍)", size=25, color="#ff4b4b"),
                        Node(id="Fact", label="전통 한복 원형", size=20, color="#4CAF50"),
                        Node(id="Art", label="조선시대 풍속화", size=15, color="#9467bd"),
                        Node(id="Point", label="시각 고증 불일치 판정", size=20, color=POINT_COLOR)
                    ],
                    "edges": [
                        Edge(source="Job", target="Issue", label="양식 혼용"),
                        Edge(source="Job", target="Fact", label="사료 기반 원형"),
                        Edge(source="Fact", target="Art", label="시각적 실증"),
                        Edge(source="Issue", target="Point", label="교차 검증 완료")
                    ]
                }
            }

            cur = issue_data.get(st.session_state.selected_issue, issue_data["서양 사제"])
            config = Config(width=650, height=400, directed=True, nodeHighlightBehavior=True,
                            staticGraph=False, collapsible=False,
                            node={"labelProperty": "label", "renderLabel": True},
                            link={"labelProperty": "label", "renderLabel": True})
            agraph(nodes=cur["nodes"], edges=cur["edges"], config=config)
