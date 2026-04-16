import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import io

# 1. 페이지 설정
st.set_page_config(page_title="문항 특성 분석 시스템 v3.2", page_icon="🎓", layout="wide")

# 2. 스타일 설정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;
    }
    </style>
    <div class="main-header">
        <h1>🎓 과목별 문항 특성 분석 시스템  v3.2</h1>
        <p>국어·수학·영어 과목별 3단계 분석 체계</p>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 구조 초기화 (세션 상태)
SUBJECTS = ['국어', '사회', '수학', '과학', '영어']
# 모든 교과의 범주를 포괄하도록 대범주 리스트 구성
GRAND_CATEGORIES = ["영역", "인지 유형", "역량", "문제 상황 유형", "자료 제시 유형", "기술공학적 기능", "지문 특성", "보기(자료) 형태", "문항 세부 특성", "기타"]

if 'results' not in st.session_state:
    st.session_state.results = {}

if 'config' not in st.session_state:
    st.session_state.config = {sub: {gc: {} for gc in GRAND_CATEGORIES} for sub in SUBJECTS}
    
    # --- [국어] 초기 세팅 반영 [cite: 3] ---
    st.session_state.config['국어']['영역'] = {
        "듣기·말하기": ["대화 원리 고려하여 대화하기", "논증의 타당성 평가하며 토론하기", "청중의 관심과 요구 고려하여 발표하기", "대안 탐색하며 협상하기"],
        "읽기": ["논증의 타당성 평가하기", "관점, 의도, 표현 평가하기", "주제 통합적으로 읽기", "사회적 독서 활동에 참여하기"],
        "쓰기": ["사회적 쟁점에 대한 견해 표현하기", "개성이 드러나는 글 쓰기", "논증하는 글 쓰기", "정보를 종합하여 보고서 쓰기"],
        "문법": ["음운 변동", "문법 요소", "어휘의 표현과 효과", "국어의 역사성", "한글 맞춤법의 원리"]
    }
    st.session_state.config['국어']['인지 유형'] = {"인지 유형": ["기억", "이해", "적용", "분석", "평가", "창안"]}
    st.session_state.config['국어']['역량'] = {
        "비판적·창의적 사고 역량": ["비판적·창의적 이해", "비판적·창의적 표현"],
        "디지털·미디어 역량": ["디지털·미디어 자료·정보 분석과 수용", "디지털·미디어 자료·정보 활용과 생산"],
        "의사소통 역량": ["의사소통 맥락을 고려한 이해 전략 활용", "의사소통 맥락을 고려한 표현 전략 활용"]
    }
    st.session_state.config['국어']['문제 상황 유형'] = {"평가틀 맥락": ["개인적 맥락", "사회적 맥락", "학습 맥락"]}
    st.session_state.config['국어']['자료 제시 유형'] = {"자료 탐색 유형": ["단순 제시형", "정보 활용형", "미디어 활용형", "도구 조작 시뮬레이션"]}
    st.session_state.config['국어']['기술공학적 기능'] = {"기술공학적 기능": ["라디오버튼", "체크박스", "짝 연결하기", "아래로 펼치기", "핫스폿", "끌어놓기(자료연결형)", "끌어놓기(순서배열형)", "단답 입력", "서술 입력"]}
    st.session_state.config['국어']['지문 특성'] = {
        "듣기·말하기": ["대화", "발표", "토론", "협상"],
        "읽기/장르": ["정보를 전달하는 글", "설득하는 글", "정서 표현 글"],
        "문학/장르": ["서정", "서사", "극", "교술"]
    }
    st.session_state.config['국어']['보기(자료) 형태'] = {"보기 형태": ["보기(자료) 없음", "추가 자료 제시", "적용 상황 제시", "학생 반응 제시"]}

    # --- [수학] 초기 세팅 반영 [cite: 3, 4] ---
    st.session_state.config['수학']['영역'] = {
        "수와 연산": ["집합", "명제", "복소수"],
        "변화와 관계": ["다항식의 연산", "나머지정리", "인수분해", "함수", "유리함수와 무리함수"],
        "도형과 측정": ["평면좌표", "직선의 방정식", "원의 방정식", "도형의 이동"],
        "자료와 가능성": ["합의 법칙과 곱의 법칙", "순열과 조합"]
    }
    st.session_state.config['수학']['인지 유형'] = {"인지 유형": ["기억", "이해", "적용", "분석", "평가", "창안"]}
    st.session_state.config['수학']['역량'] = {
        "계산·이해": ["계산", "이해"],
        "문제해결·연결": ["문제이해 및 전략탐색", "실행 및 반성", "수학 내적 연결", "수학 외적 연결"],
        "추론": ["개연추론", "연역추론"],
        "의사소통": ["수학적 표현", "수학적 설명"],
        "정보처리": ["정보 분석 및 활용", "교구 및 공학 도구 활용"]
    }
    st.session_state.config['수학']['문제 상황 유형'] = {"평가틀 맥락": ["실생활", "학문"]}
    st.session_state.config['수학']['자료 제시 유형'] = {
        "자료 탐색 유형": ["단순 제시형", "정보 활용형", "미디어 활용형", "도구 조작 시뮬레이션"],
        "문항 표현": ["수식 및 기호", "표", "그래프/도식", "도형", "문장제", "대화"]
    }
    st.session_state.config['수학']['기술공학적 기능'] = {"기술공학적 기능": ["라디오버튼", "체크박스", "짝 연결하기", "아래로 펼치기", "핫스폿", "단답 입력", "서술 입력"]}

    # --- [영어] 초기 세팅 반영 (오류 수정됨) [cite: 19, 20, 21] ---
    st.session_state.config['영어']['영역'] = {
        "듣기": ["세부 정보 파악", "주제/요지 파악", "심정/의도 추론", "논리적 관계 파악", "함축적 의미 추론"],
        "말하기": ["자료 활용 설명", "사실적 정보 전달", "경험/계획 말하기", "의견/감정 표현", "요약하기"],
        "읽기": ["세부 정보 파악", "주제/요지 파악", "의도 추론", "논리적 관계 파악", "의견 비판적 이해"],
        "쓰기": ["자료 활용 기술", "정보 전달", "경험 기술", "의견 표현", "요약 기술"]
    }
    st.session_state.config['영어']['인지 유형'] = {"인지 유형": ["기억", "이해", "적용", "분석", "평가", "창안"]}
    st.session_state.config['영어']['역량'] = {
        "협력적 소통 역량": ["이해 능력", "표현 능력"],
        "지식정보처리 역량": ["정보수집", "정보분석", "정보활용"],
        "공동체 역량": ["다양성 이해", "문화정체성 함양"]
    }
    st.session_state.config['영어']['문제 상황 유형'] = {
        "주제": ["개인·일상생활 관련", "사회·공공생활 관련", "학업·전문지식 관련"],
        "의사소통 상황": ["개인적", "공공적", "학술적"]
    }
    st.session_state.config['영어']['자료 제시 유형'] = {"자료 유형": ["음성", "영상", "지문", "복합 자료"]}
    st.session_state.config['영어']['기술공학적 기능'] = {"기술공학적 기능": ["라디오버튼", "체크박스", "짝 연결하기", "아래로 펼치기", "핫스폿", "끌어놓기", "단답/서술 입력"]}
    st.session_state.config['영어']['문항 세부 특성'] = {
        "지문 유형(장르)": ["설명(expository)", "논술(argumentative)", "묘사(descriptive)", "서사(narrative)"],
        "담화 구조": ["독백(monologue)", "대화(dialogue)"],
        "지문의 수": ["단일 지문", "복합 지문"],
        "문제 해결 요소": ["발문 명시성", "소재 친숙성", "흐름 일관성", "단서 명시성", "정답 2개 이상", "매력적 오답 유무"]
    }

# 4. 사이드바: 파일 업로드
with st.sidebar:
    st.header("⚙️ 시스템 관리")
    uploaded_files = st.file_uploader("🖼️ 문항 이미지 업로드", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if st.button("🔄 데이터 초기화"):
        st.session_state.results = {}
        st.rerun()

# 5. 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["⚙️ 과목별 항목 설정", "📝 문항 분석", "📊 결과 내보내기"])

# --- 탭 1: 설정 ---
with tab1:
    st.subheader("📋 과목별 3단계 계층 설정")
    sel_sub_config = st.selectbox("설정할 과목 선택", SUBJECTS)
    cols = st.columns(2)
    for i, gc in enumerate(GRAND_CATEGORIES):
        with cols[i % 2]:
            current_data = st.session_state.config[sel_sub_config][gc]
            default_text = "\n".join([f"{mid}: {', '.join(subs)}" for mid, subs in current_data.items()])
            input_text = st.text_area(f"📍 {gc}", value=default_text, height=150, key=f"set_{sel_sub_config}_{gc}")
            parsed_gc = {}
            for line in input_text.split('\n'):
                if ':' in line:
                    mid, subs = line.split(':', 1)
                    parsed_gc[mid.strip()] = [s.strip() for s in subs.split(',') if s.strip()]
            st.session_state.config[sel_sub_config][gc] = parsed_gc
    if st.button("💾 설정 저장"): st.success(f"{sel_sub_config} 설정이 임시 저장되었습니다.")

# --- 탭 2: 문항 분석 ---
with tab2:
    if not uploaded_files:
        st.warning("왼쪽 사이드바에서 이미지를 먼저 업로드해주세요.")
    else:
        sub_col, file_col = st.columns(2)
        with sub_col: selected_subject = st.selectbox("📚 분석 교과", SUBJECTS)
        with file_col: selected_file = st.selectbox("🔍 분석 문항", [f.name for f in uploaded_files])
        
        target = next(f for f in uploaded_files if f.name == selected_file)
        c_img, c_in = st.columns([1, 1])
        with c_img: st.image(target, use_container_width=True)
        with c_in:
            st.subheader(f"✅ 특성 입력 ({selected_subject})")
            res_key = f"{selected_subject}_{selected_file}"
            current_res = st.session_state.results.get(res_key, {})
            new_res = {'파일명': selected_file, '교과': selected_subject}
            
            for gc in GRAND_CATEGORIES:
                m_data = st.session_state.config[selected_subject][gc]
                if m_data:
                    with st.expander(f"🔹 {gc}"):
                        for mid, subs in m_data.items():
                            st.markdown(f"**[{mid}]**")
                            inner_cols = st.columns(2)
                            for idx, s in enumerate(subs):
                                k = f"{gc}::{mid}::{s}"
                                with inner_cols[idx % 2]:
                                    checked = st.checkbox(s, value=bool(current_res.get(k, 0)), key=f"ch_{res_key}_{k}")
                                    new_res[k] = 1 if checked else 0
            if st.button("💾 분석 결과 저장", type="primary", use_container_width=True):
                new_res['저장시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.results[res_key] = new_res
                st.toast(f"{selected_file} 저장 완료!")

# --- 탭 3: 결과 내보내기 ---
with tab3:
    if not st.session_state.results:
        st.info("데이터가 없습니다. 분석 탭에서 저장을 먼저 진행해주세요.")
    else:
        df = pd.DataFrame.from_dict(st.session_state.results, orient='index')
        cols = list(df.columns)
        main_order = ['파일명', '교과', '저장시간']
        ordered = [c for c in main_order if c in cols] + [c for c in cols if c not in main_order]
        df = df[ordered]
        st.dataframe(df, use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='분석결과')
        st.download_button("📥 엑셀 파일 다운로드", data=output.getvalue(), file_name=f"분석결과_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")