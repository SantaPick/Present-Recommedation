"""
심리테스트 응답을 가중치로 변환하는 계산기
"""
import pandas as pd
from pathlib import Path

class ScoringCalculator:
    def __init__(self):
        # 상대경로 설정
        self.base_path = Path("data/psychology-question")
        
        # 참조 파일들 로드
        self.choice_2_data = pd.read_csv(self.base_path / "2-choice-question.csv")
        self.choice_4_data = pd.read_csv(self.base_path / "4-choice-question.csv")
        self.choice_5_data = pd.read_csv(self.base_path / "5-point-question.csv")
        self.choice_ox_data = pd.read_csv(self.base_path / "O-X-question.csv")
        self.emotion_concept_data = pd.read_csv(self.base_path / "emotion-concept-relation.csv")
        
    def calculate_user_weights(self, answers):
        """사용자 답변을 기반으로 노드별 가중치 계산"""
        user_weights = {}
        
        for answer_id, answer_data in answers.items():
            question_type = answer_data['question_type']
            target_node = answer_data['target_node']
            selected_choice = answer_data['selected_choice']
            choice_index = answer_data['choice_index']
            question = answer_data['question']
            
            # 질문 타입별 가중치 계산
            if question_type == "5_point_question":
                weight = self._calculate_5point_weight(question, selected_choice, choice_index, target_node)
            elif question_type == "2_choice_question":
                weight = self._calculate_2choice_weight(question, choice_index)
            elif question_type == "4_choice_question":
                weight = self._calculate_4choice_weight(question, choice_index)
            elif question_type == "O_X_question":
                weight = self._calculate_ox_weight(question, choice_index)
            else:
                continue
                
            # 가중치 저장
            if target_node not in user_weights:
                user_weights[target_node] = []
            user_weights[target_node].append(weight)
        
        # 동일 노드의 다중 질문은 평균값 사용
        final_weights = {}
        for node, weights in user_weights.items():
            final_weights[node] = sum(weights) / len(weights)
        
        # Pref_ 노드 처리
        self._process_pref_nodes(final_weights)
        
        # 가중치 범위 클리핑 (-1 ~ 1)
        for node in final_weights:
            final_weights[node] = max(-1.0, min(1.0, final_weights[node]))
            
        return final_weights
    
    def _calculate_5point_weight(self, question, selected_choice, choice_index, target_node):
        """5-point 질문 가중치 계산"""
        # 1->0.2, 2->0.4, 3->0.6, 4->0.8, 5->1.0
        base_weight = (choice_index + 1) * 0.2
        
        # positive_negative_relation 확인
        relation_row = self.choice_5_data[self.choice_5_data['question'] == question]
        if not relation_row.empty:
            relation = relation_row.iloc[0]['positive_negative_relation']
            if relation == '-':
                base_weight = -base_weight
        
        return base_weight
    
    def _calculate_2choice_weight(self, question, choice_index):
        """2-choice 질문 가중치 계산"""
        relation_row = self.choice_2_data[self.choice_2_data['question'] == question]
        if not relation_row.empty:
            row = relation_row.iloc[0]
            if choice_index == 0:  # response_1
                return 0.7 if row['pn_response_1'] == '+' else -0.7
            else:  # response_2
                return 0.7 if row['pn_response_2'] == '+' else -0.7
        return 0.0
    
    def _calculate_4choice_weight(self, question, choice_index):
        """4-choice 질문 가중치 계산"""
        relation_row = self.choice_4_data[self.choice_4_data['question'] == question]
        if not relation_row.empty:
            row = relation_row.iloc[0]
            pn_col = f'pn_response_{choice_index + 1}'
            if pn_col in row:
                return 0.7 if row[pn_col] == '+' else -0.7
        return 0.0
    
    def _calculate_ox_weight(self, question, choice_index):
        """O-X 질문 가중치 계산"""
        relation_row = self.choice_ox_data[self.choice_ox_data['question'] == question]
        if not relation_row.empty:
            row = relation_row.iloc[0]
            if choice_index == 0:  # O
                return 0.7 if row['pn_response_1'] == '+' else -0.7
            else:  # X
                return 0.7 if row['pn_response_2'] == '+' else -0.7
        return 0.0
    
    def _process_pref_nodes(self, weights):
        """Pref_ 노드 처리 및 다른 concept 노드에 영향 적용"""
        pref_nodes = [node for node in weights.keys() if node.startswith('Pref_')]
        
        for pref_node in pref_nodes:
            # Pref_Elegant -> Elegant
            emotion_name = pref_node.replace('Pref_', '')
            pref_weight = weights[pref_node]
            
            # emotion-concept-relation.csv에서 관계 확인
            emotion_row = self.emotion_concept_data[
                self.emotion_concept_data['Emotion'] == f'[{emotion_name}]'
            ]
            
            if not emotion_row.empty:
                row = emotion_row.iloc[0]
                
                # 각 concept에 대해 관계 확인
                concept_columns = [
                    'Texture_Softness', 'Texture_Smoothness', 'Brand', 
                    'Color_Brightness', 'Color_Saturation', 'Simple', 
                    'Glossiness', 'Color_Temperature'
                ]
                
                for concept in concept_columns:
                    if concept in row and pd.notna(row[concept]):
                        relation = row[concept]
                        if relation in ['+', '-']:
                            # 1->0.05, 2->0.1, 3->0.15, 4->0.2, 5->0.25
                            # pref_weight는 이미 0.2~1.0 범위이므로 이를 기반으로 계산
                            additional_weight = pref_weight * 0.25  # 최대 0.25
                            if relation == '-':
                                additional_weight = -additional_weight
                            
                            # 기존 가중치에 추가
                            if concept in weights:
                                weights[concept] += additional_weight
                            else:
                                weights[concept] = additional_weight
            
            # Pref_ 노드를 실제 노드명으로 변경
            weights[emotion_name] = weights.pop(pref_node)

# 테스트 코드
if __name__ == "__main__":
    calculator = ScoringCalculator()
    
    # 테스트 답변 데이터
    test_answers = {
        'trait_0': {
            'question': '남들의 주목을 받는 것이 딱히 부담스럽지 않고 개의치 않는다.',
            'question_type': '5_point_question',
            'target_node': 'Extraversion',
            'selected_choice': '4',
            'choice_index': 3
        }
    }
    
    weights = calculator.calculate_user_weights(test_answers)
    print("계산된 가중치:", weights)