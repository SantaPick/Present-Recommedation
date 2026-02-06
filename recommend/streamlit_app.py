"""
심리테스트 Streamlit 웹 애플리케이션
"""
import streamlit as st
import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from data_loader import PsychologyDataLoader
from scoring_calculator import ScoringCalculator
from recommendation_engine import RecommendationEngine
from pathlib import Path

def initialize_session_state():
    """세션 상태 초기화"""
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = PsychologyDataLoader()
        st.session_state.questions = st.session_state.data_loader.create_question_structure()
    
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False

def display_progress():
    """진행률 표시"""
    total_questions = len(st.session_state.questions)
    current_idx = st.session_state.current_question_idx
    progress = current_idx / total_questions
    
    st.progress(progress)
    st.write(f"**진행률**: {current_idx}/{total_questions} ({progress*100:.1f}%)")

def display_current_question():
    """현재 질문 표시"""
    if st.session_state.current_question_idx >= len(st.session_state.questions):
        st.session_state.test_completed = True
        return
    
    current_q = st.session_state.questions[st.session_state.current_question_idx]
    
    # 질문 정보 표시
    st.subheader(f"질문 {st.session_state.current_question_idx + 1}")
    
    # 카테고리 표시
    category_name = "성격 특성" if current_q['category'] == 'trait' else "제품 선호도"
    st.write(f"**카테고리**: {category_name}")
    
    # 질문 텍스트
    st.write("### " + current_q['question'])
    
    # 선택지 표시 (라디오 버튼)
    answer_key = f"question_{st.session_state.current_question_idx}"
    
    # 기존 답변이 있는지 확인
    existing_answer = st.session_state.answers.get(current_q['id'])
    default_index = 0
    if existing_answer and existing_answer['selected_choice'] in current_q['choices']:
        default_index = current_q['choices'].index(existing_answer['selected_choice'])
    
    selected_choice = st.radio(
        "답변을 선택해주세요:",
        options=current_q['choices'],
        key=answer_key,
        index=default_index
    )
    
    # 답변 저장 (항상 저장, 라디오 버튼은 항상 값이 있음)
    st.session_state.answers[current_q['id']] = {
        'question': current_q['question'],
        'question_type': current_q['question_type'],
        'target_node': current_q['target_node'],
        'category': current_q['category'],
        'selected_choice': selected_choice,
        'choice_index': current_q['choices'].index(selected_choice)
    }

def navigation_buttons():
    """네비게이션 버튼들"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_question_idx > 0:
            if st.button("이전 질문"):
                st.session_state.current_question_idx -= 1
                st.experimental_rerun()
    
    with col2:
        st.success("답변 완료")
    
    with col3:
        # 다음 버튼 또는 완료 버튼 (라디오 버튼은 항상 답변이 있으므로 항상 활성화)
        if st.session_state.current_question_idx < len(st.session_state.questions) - 1:
            if st.button("다음 질문"):
                st.session_state.current_question_idx += 1
                st.experimental_rerun()
        else:
            if st.button("테스트 완료"):
                st.session_state.test_completed = True
                st.experimental_rerun()

def display_results():
    """결과 표시 및 가중치 계산"""
    st.success("심리테스트가 완료되었습니다!")
    
    # 가중치 계산
    if 'user_weights' not in st.session_state:
        calculator = ScoringCalculator()
        st.session_state.user_weights = calculator.calculate_user_weights(st.session_state.answers)
    
    st.subheader("계산된 가중치")
    
    # Trait 노드와 Concept 노드 분리
    trait_weights = {}
    concept_weights = {}
    
    for node, weight in st.session_state.user_weights.items():
        # 간단한 분류 (실제로는 entity_list.txt를 참조해야 하지만 임시로)
        if node in ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism',
                   'Elegant', 'Cute', 'Modern', 'Luxurious', 'Warm', 'Vivid', 'Sharp',
                   'OSL', 'CNFU', 'MVS', 'CVPA']:
            trait_weights[node] = weight
        else:
            concept_weights[node] = weight
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Trait 노드 가중치**")
        for node, weight in trait_weights.items():
            st.write(f"{node}: {weight:.3f}")
    
    with col2:
        st.write("**Concept 노드 가중치**")
        for node, weight in concept_weights.items():
            st.write(f"{node}: {weight:.3f}")
    
    # 답변 상세 (접기/펼치기)
    with st.expander("상세 답변 보기"):
        trait_answers = [a for a in st.session_state.answers.values() if a['category'] == 'trait']
        concept_answers = [a for a in st.session_state.answers.values() if a['category'] == 'concept']
        
        st.write(f"성격 특성 질문: {len(trait_answers)}개")
        st.write(f"제품 선호도 질문: {len(concept_answers)}개")
        
        for q_id, answer in st.session_state.answers.items():
            st.write(f"**{answer['question']}**")
            st.write(f"답변: {answer['selected_choice']}")
            st.write(f"노드: {answer['target_node']} ({answer['category']})")
            st.write("---")
    
    # 추천 생성 버튼
    if st.button("추천 받기"):
        with st.spinner("추천을 생성하는 중..."):
            try:
                engine = RecommendationEngine()
                user_id = engine.add_user_node(st.session_state.user_weights)
                recommendations = engine.get_recommendations(user_id, top_k=10)
                recommendations = engine.get_item_details(recommendations)
                
                st.session_state.recommendations = recommendations
                st.session_state.user_id = user_id
                
            except Exception as e:
                st.error(f"추천 생성 실패: {e}")
    
    # 추천 결과 표시
    if 'recommendations' in st.session_state:
        st.subheader("추천 상품")
        
        if st.session_state.recommendations:
            for i, rec in enumerate(st.session_state.recommendations, 1):
                product_name = rec.get('name', f'상품 {rec["item_id"]}')
                st.subheader(f"{i}. {product_name}")
                st.write(f"**유사도**: {rec['similarity']:.3f}")
                
                # 상품 상세 정보를 접기/펼치기로 표시
                with st.expander("상품 상세 정보"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        # 상품 이미지 표시
                        if rec.get('image_path') and Path(rec['image_path']).exists():
                            st.image(rec['image_path'], width=200)
                        else:
                            st.write("이미지 없음")
                        
                        st.write(f"**상품 ID**: {rec['item_id']}")
                        st.write(f"**가격**: {rec.get('price', 'N/A')}")
                        st.write(f"**카테고리**: {rec.get('category', 'N/A')}")
                    with col2:
                        st.write(f"**상품명**: {rec.get('name', rec['item_name'])}")
                        st.write(f"**설명**: {rec.get('description', 'N/A')}")
        else:
            st.write("추천할 상품이 없습니다.")
    
    # 다시 시작 버튼
    if st.button("다시 테스트하기"):
        for key in ['current_question_idx', 'answers', 'test_completed', 'user_weights', 'recommendations', 'user_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

def main():
    """메인 애플리케이션"""
    st.set_page_config(
        page_title="🎁 SantaPick 심리테스트",
        page_icon="🎁",
        layout="wide"
    )
    
    # 초기화
    initialize_session_state()
    
    # 헤더
    st.title("🎁 SantaPick 심리테스트")
    st.write("당신의 성격과 선호도를 분석하여 맞춤형 선물을 추천해드립니다!")
    
    # 메인 컨텐츠
    if not st.session_state.test_completed:
        # 진행률 표시
        display_progress()
        
        st.write("---")
        
        # 현재 질문 표시
        display_current_question()
        
        st.write("---")
        
        # 네비게이션
        navigation_buttons()
        
    else:
        # 결과 표시
        display_results()

if __name__ == "__main__":
    main()