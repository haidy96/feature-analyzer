import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import io

# 1. 페이지 설정
st.set_page_config(page_title="문항 특성 분석 시스템 v3.0", page_icon="🎓", layout="wide")

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
        <h1>🎓 과목별 문항 특성 분석 시스템</h1>
        <p>국어·사회·수학·과학·영어 과목별 맞춤형 3단계(대-중-소) 분석 체계</p>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 구조 초기화
SUBJECTS = ['국어', '사회', '수학', '과학', '영어']
GRAND_CATEGORIES = ["영역", "인지 유형", "역량", "문제 상황 유형", "자료 제시 유형", "기술공학적 기능", "지문 특성", "보기(자료) 형태", "기타"]

# 결과 저장용 세션 상태 초기화
if 'results' not in st.session_state:
    st.session_state.results = {}

if 'config' not in st.session_state:
    st.session_state.config = {sub: {gc: {} for gc in GRAND_CATEGORIES} for sub in SUBJECTS}
    
    # 국어 초기 설정
    st.session_state.config['국어']['영역'] = {"듣기·말하기": ["대화 원리 고려", "토론하기"], "읽기": ["타당성 평가", "관점 분석"], "쓰기": ["견해 표현", "보고서 쓰기"]}
    st.session_state.config['국어']['인지 유형'] = {"인지 유형": ["기억", "이해", "적용", "분석", "평가", "창안"]}
    
    # 수학 초기 설정
    st.session_state.config['수학']['영역'] = {"수와 연산": ["집합", "명제", "복소수"], "변화와 관계": ["함수", "방정식"], "도형과 측정": ["평면좌표", "원의 방정식"]}
    st.session_state.config['수학']['역량'] = {"계산·이해": ["계산", "이해"], "문제해결": ["전략탐색", "실행"], "추론": ["연역", "개연"]}

# 4. 사이드바 (파일 업로드 변수를 전역에서 쓸 수 있도록 배치)
with st.sidebar:
    st.header("⚙️ 시스템 관리")
    uploaded_files = st.file_uploader("🖼️ 문항 이미지 업로드", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if st.button("🔄 데이터 초기화"):
        st.session_state.results = {}
        st.rerun()

# 5. 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["⚙️ 과목별 항목 설정", "📝 문항 분석", "📊 결과 내보내기"])

# --- 탭 1: 항목 설정 ---
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
    if st.button("💾 설정 저장"): st.success("저장 완료")

# --- 탭 2: 문항 분석 ---
with tab2:
    if not uploaded_files:
        st.warning("왼쪽 사이드바에서 이미지를 먼저 업로드해주세요.")
    else:
        sub_col, file_col = st.columns(2)
        with sub_col: selected_subject = st.selectbox("📚 교과 선택", SUBJECTS)
        with file_col: selected_file = st.selectbox("🔍 문항 선택", [f.name for f in uploaded_files])
        
        target = next(f for f in uploaded_files if f.name == selected_file)
        c_img, c_in = st.columns([1, 1])
        with c_img: st.image(target, use_container_width=True)
        with c_in:
            st.subheader(f"✅ 특성 입력 ({selected_subject})")
            res_key = f"{selected_subject}_{selected_file}"
            current_res = st.session_state.results.get(res_key, {})
            new_res = {'파일명': selected_file, '교과': selected_subject}
            
            for gc in GRAND_CATEGORIES:
                with st.expander(f"🔹 {gc}"):
                    m_data = st.session_state.config[selected_subject][gc]
                    for mid, subs in m_data.items():
                        st.markdown(f"**[{mid}]**")
                        for s in subs:
                            k = f"{gc}::{mid}::{s}"
                            checked = st.checkbox(s, value=bool(current_res.get(k, 0)), key=f"ch_{res_key}_{k}")
                            new_res[k] = 1 if checked else 0
            if st.button("💾 분석 결과 저장"):
                new_res['저장시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.results[res_key] = new_res
                st.success(f"{selected_file} 저장 완료!")

# --- 탭 3: 결과 내보내기 (수정 완료) ---
with tab3:
    if not st.session_state.results:
        st.info("저장된 분석 결과가 없습니다. '문항 분석' 탭에서 저장을 먼저 진행해주세요.")
    else:
        st.subheader("📊 분석 결과 데이터프레임")
        
        # 1. 데이터프레임 생성
        df = pd.DataFrame.from_dict(st.session_state.results, orient='index')
        
        # 2. 열 순서 정리 (기본 정보 우선 표시)
        cols = list(df.columns)
        if '저장시간' in cols:
            cols.insert(0, cols.pop(cols.index('저장시간')))
        if '파일명' in cols:
            cols.insert(0, cols.pop(cols.index('파일명')))
        df = df[cols]
        
        # 3. 화면 표시
        st.dataframe(df, use_container_width=True)
        
        # 4. 엑셀 다운로드 처리
        try:
            output = io.BytesIO()
            # engine='openpyxl'을 명시적으로 사용
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 분석 결과 엑셀로 받기",
                data=processed_data,
                file_name=f"분석결과_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"엑셀 생성 중 오류가 발생했습니다: {e}")
            st.info("라이브러리 설치 확인이 필요할 수 있습니다. 터미널에 'pip install openpyxl'을 입력해보세요.")