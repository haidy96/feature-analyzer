import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import datetime
import io

# 1. 페이지 기본 설정
st.set_page_config(page_title="문항 특성 분석 시스템", page_icon="🎓", layout="wide")

# 2. 스타일 설정 (기존 Notebook의 세련된 디자인 반영)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;
    }
    .status-box {
        background-color: #f8f9fa; border-left: 5px solid #667eea; padding: 1rem; border-radius: 5px;
    }
    </style>
    <div class="main-header">
        <h1>🎓 문항 특성 분석 시스템 v2.0</h1>
        <p>7개 고정 대범주 × 사용자 정의 하위 항목 분석</p>
    </div>
""", unsafe_allow_html=True)

# 3. 세션 상태 초기화 (데이터 보존용)
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'config' not in st.session_state:
    # 기본 템플릿 설정
    st.session_state.config = {
        "영역": ["수와 연산", "문자와 식", "함수", "기하", "확률과 통계"],
        "인지 유형": ["계산", "이해", "추론", "문제해결", "증명", "모델링"],
        "역량": ["문제해결능력", "추론능력", "창의융합능력", "의사소통능력", "정보처리능력"],
        "문제 상황 유형": ["수학적 상황", "실생활 상황(개인)", "실생활 상황(사회)", "학문적 상황"],
        "자료 제시 유형": ["수식", "그림/도형", "표/그래프", "문장제", "복합자료"],
        "기술공학적 기능": ["계산기 활용", "소프트웨어 활용", "교구 활용", "해당없음"],
        "기타": ["선택형", "단답형", "서술형", "논술형", "고난도"]
    }

# 4. 사이드바: 설정 및 파일 업로드
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    subject = st.text_input("📚 교과명", value="사회")
    
    st.divider()
    
    st.subheader("🖼️ 분석 대상 업로드")
    uploaded_files = st.file_uploader("문항 이미지를 선택하세요", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)}개의 파일이 로드되었습니다.")

    st.divider()
    
    if st.button("🔄 전체 설정 초기화"):
        st.session_state.results = {}
        st.rerun()

# 5. 메인 화면: 탭 구성 (설정 / 분석 / 결과)
tab1, tab2, tab3 = st.tabs(["⚙️ 하위 항목 설정", "📝 문항 분석", "📊 결과 내보내기"])

# --- 탭 1: 하위 항목 설정 ---
with tab1:
    st.subheader("📋 대범주별 하위 항목 편집")
    st.info("각 대범주에 속할 항목을 한 줄에 하나씩 입력하세요. (최대 40개)")
    
    cols = st.columns(2)
    new_config = {}
    categories = list(st.session_state.config.keys())
    
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            current_val = "\n".join(st.session_state.config[cat])
            text_area_val = st.text_area(f"📍 {cat}", value=current_val, height=150, key=f"setup_{cat}")
            new_config[cat] = [item.strip() for item in text_area_val.split('\n') if item.strip()]
            
    if st.button("💾 설정 저장하기", type="primary"):
        st.session_state.config = new_config
        st.success("설정이 저장되었습니다. '문항 분석' 탭으로 이동하세요!")

# --- 탭 2: 문항 분석 ---
with tab2:
    if not uploaded_files:
        st.warning("먼저 왼쪽 사이드바에서 이미지를 업로드해주세요.")
    else:
        # 파일 선택 드롭다운
        file_names = [f.name for f in uploaded_files]
        selected_file_name = st.selectbox("분석할 문항 선택", file_names)
        
        # 선택된 파일 객체 찾기
        target_file = next(f for f in uploaded_files if f.name == selected_file_name)
        
        col_img, col_input = st.columns([1, 1])
        
        with col_img:
            image = Image.open(target_file)
            st.image(image, caption=f"고유번호: {selected_file_name}", use_container_width=True)
            
        with col_input:
            st.subheader(f"🔍 특성 체크: {selected_file_name}")
            
            # 입력 데이터 구조 생성
            current_entry = st.session_state.results.get(selected_file_name, {})
            new_entry_data = {}
            
            # 카테고리별 아코디언 배치
            for cat in st.session_state.config:
                with st.expander(f"{cat} ({len(st.session_state.config[cat])}개)"):
                    cat_items = st.session_state.config[cat]
                    # 2열 배치
                    inner_cols = st.columns(2)
                    for idx, item in enumerate(cat_items):
                        key = f"{cat}::{item}"
                        # 기존 저장값 불러오기 (없으면 False)
                        with inner_cols[idx % 2]:
                            is_checked = st.checkbox(item, value=bool(current_entry.get(key, 0)), key=f"input_{selected_file_name}_{key}")
                            new_entry_data[key] = 1 if is_checked else 0
            
            if st.button("💾 현재 문항 저장", type="primary", use_container_width=True):
                new_entry_data['파일명'] = selected_file_name
                new_entry_data['저장시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.results[selected_file_name] = new_entry_data
                st.toast(f"{selected_file_name} 저장 완료!")

# --- 탭 3: 결과 내보내기 ---
with tab3:
    if not st.session_state.results:
        st.info("저장된 데이터가 없습니다. 분석을 먼저 진행해주세요.")
    else:
        st.subheader("📊 분석 결과 미리보기")
        
        # 데이터프레임 변환
        df = pd.DataFrame.from_dict(st.session_state.results, orient='index')
        
        # 컬럼 순서 정리 (파일명, 저장시간 우선)
        fixed_cols = ['파일명', '저장시간']
        feature_cols = [c for c in df.columns if '::' in c]
        df = df[fixed_cols + feature_cols]
        
        # 화면 표시용 컬럼명 간소화 (대범주 제거)
        display_df = df.rename(columns={c: c.split('::')[1] for c in feature_cols})
        st.dataframe(display_df, use_container_width=True)
        
        # 엑셀 다운로드 버튼
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=True, index_label="고유번호", sheet_name='분석결과')
        
        st.download_button(
            label="📥 엑셀 파일 다운로드",
            data=output.getvalue(),
            file_name=f"{subject}_문항특성분석_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# 6. 하단 진행 상황
st.divider()
total_files = len(uploaded_files) if uploaded_files else 0
completed = len(st.session_state.results)
progress = completed / total_files if total_files > 0 else 0
st.progress(progress, text=f"진행도: {completed} / {total_files} 문항 완료")