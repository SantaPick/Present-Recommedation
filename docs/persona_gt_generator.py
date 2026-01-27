"""
페르소나 기반 Ground Truth 생성기
심리 프로필 → 선물 선호도 매핑을 통한 합성 데이터 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class PersonaGTGenerator:
    def __init__(self):
        self.personas = self._define_personas()
        self.item_categories = self._load_item_categories()
        
    def _define_personas(self) -> Dict:
        """심리학 이론 기반 페르소나 정의"""
        return {
            # 외향성 높음 + 개방성 높음
            "social_explorer": {
                "traits": {
                    "extraversion": 0.85,
                    "openness": 0.80,
                    "agreeableness": 0.70,
                    "conscientiousness": 0.50,
                    "emotional_stability": 0.60
                },
                "preferences": {
                    "categories": {
                        "파티용품": 0.9,
                        "소셜게임": 0.8, 
                        "케이크": 0.9,
                        "와인・위스키": 0.7,
                        "독서용품": 0.2,
                        "개인취미": 0.3
                    },
                    "concepts": {
                        "social": 0.9,
                        "entertainment": 0.8,
                        "warm_color": 0.7,
                        "premium_brand": 0.6
                    }
                }
            },
            
            # 내향성 높음 + 개방성 높음  
            "creative_introvert": {
                "traits": {
                    "extraversion": 0.20,
                    "openness": 0.90,
                    "agreeableness": 0.60,
                    "conscientiousness": 0.70,
                    "emotional_stability": 0.50
                },
                "preferences": {
                    "categories": {
                        "예술용품": 0.9,
                        "핸드메이드": 0.8,
                        "독서용품": 0.8,
                        "개인취미": 0.9,
                        "파티용품": 0.1,
                        "소셜게임": 0.2
                    },
                    "concepts": {
                        "handmade": 0.9,
                        "functional": 0.7,
                        "cool_color": 0.8,
                        "relaxation": 0.8
                    }
                }
            },
            
            # 성실성 높음 + 개방성 낮음
            "practical_organizer": {
                "traits": {
                    "extraversion": 0.50,
                    "openness": 0.30,
                    "agreeableness": 0.70,
                    "conscientiousness": 0.90,
                    "emotional_stability": 0.80
                },
                "preferences": {
                    "categories": {
                        "가전제품": 0.9,
                        "정리용품": 0.9,
                        "실용도구": 0.8,
                        "건강식품": 0.7,
                        "예술용품": 0.2,
                        "장식품": 0.3
                    },
                    "concepts": {
                        "functional": 0.9,
                        "premium_brand": 0.7,
                        "eco_certified": 0.6,
                        "entertainment": 0.3
                    }
                }
            },
            
            # 친화성 높음 + 정서안정성 낮음
            "caring_worrier": {
                "traits": {
                    "extraversion": 0.60,
                    "openness": 0.60,
                    "agreeableness": 0.90,
                    "conscientiousness": 0.60,
                    "emotional_stability": 0.30
                },
                "preferences": {
                    "categories": {
                        "꽃다발": 0.9,
                        "향수・바디": 0.8,
                        "건강식품": 0.8,
                        "홈웨어": 0.7,
                        "와인・위스키": 0.3,
                        "전자제품": 0.4
                    },
                    "concepts": {
                        "relaxation": 0.9,
                        "warm_color": 0.8,
                        "texture_soft": 0.8,
                        "social": 0.7
                    }
                }
            },
            
            # 물질주의 높음
            "luxury_seeker": {
                "traits": {
                    "extraversion": 0.70,
                    "openness": 0.50,
                    "agreeableness": 0.40,
                    "conscientiousness": 0.60,
                    "emotional_stability": 0.70,
                    "materialism_centrality": 0.90,
                    "materialism_happiness": 0.80
                },
                "preferences": {
                    "categories": {
                        "패션・주얼리": 0.9,
                        "향수・바디": 0.8,
                        "전자제품": 0.8,
                        "와인・위스키": 0.7,
                        "건강식품": 0.3,
                        "도서": 0.2
                    },
                    "concepts": {
                        "premium_brand": 0.9,
                        "red": 0.7,
                        "texture_hard": 0.6,
                        "entertainment": 0.6
                    }
                }
            }
        }
    
    def _load_item_categories(self) -> Dict:
        """상품 카테고리별 특성 정의"""
        return {
            "추천선물": {"social": 0.7, "entertainment": 0.6},
            "케이크": {"social": 0.9, "entertainment": 0.8, "warm_color": 0.6},
            "꽃다발": {"relaxation": 0.8, "warm_color": 0.9, "texture_soft": 0.7},
            "패션・주얼리": {"premium_brand": 0.8, "red": 0.5, "blue": 0.5},
            "향수・바디": {"relaxation": 0.7, "premium_brand": 0.6, "texture_soft": 0.5},
            "가전제품": {"functional": 0.9, "premium_brand": 0.5, "texture_hard": 0.8},
            "건강식품": {"functional": 0.8, "eco_certified": 0.7, "relaxation": 0.6},
            "와인・위스키": {"social": 0.6, "premium_brand": 0.8, "red": 0.4},
            "골프・스포츠": {"social": 0.7, "functional": 0.6, "entertainment": 0.8},
            "팬덤・캐릭터": {"entertainment": 0.9, "warm_color": 0.7, "social": 0.5}
        }
    
    def generate_user_item_matrix(self, n_users: int = 1000, n_items: int = 500) -> pd.DataFrame:
        """페르소나 기반 사용자-아이템 선호도 매트릭스 생성"""
        
        # 사용자별 페르소나 할당 (확률적)
        persona_names = list(self.personas.keys())
        user_personas = np.random.choice(persona_names, size=n_users, 
                                       p=[0.25, 0.20, 0.20, 0.20, 0.15])  # 페르소나별 분포
        
        # 아이템별 카테고리 할당 (실제 데이터 기반)
        categories = list(self.item_categories.keys())
        item_categories = np.random.choice(categories, size=n_items,
                                         p=[0.15, 0.10, 0.12, 0.15, 0.08, 0.10, 0.08, 0.05, 0.08, 0.09])
        
        # 선호도 매트릭스 생성
        preference_matrix = np.zeros((n_users, n_items))
        
        for user_idx, persona_name in enumerate(user_personas):
            persona = self.personas[persona_name]
            
            for item_idx, category in enumerate(item_categories):
                # 기본 선호도 (카테고리 기반)
                base_preference = persona["preferences"]["categories"].get(category, 0.5)
                
                # 노이즈 추가 (개인차 반영)
                noise = np.random.normal(0, 0.1)
                preference = np.clip(base_preference + noise, 0, 1)
                
                preference_matrix[user_idx, item_idx] = preference
        
        return pd.DataFrame(preference_matrix, 
                          index=[f"user_{i}" for i in range(n_users)],
                          columns=[f"item_{i}" for i in range(n_items)])
    
    def generate_explicit_ratings(self, preference_matrix: pd.DataFrame, 
                                rating_probability: float = 0.1) -> pd.DataFrame:
        """선호도 매트릭스를 명시적 평점으로 변환"""
        
        n_users, n_items = preference_matrix.shape
        ratings = []
        
        for user_idx in range(n_users):
            for item_idx in range(n_items):
                # 평점을 남길 확률 (선호도가 높을수록 평점 남길 확률 높음)
                preference = preference_matrix.iloc[user_idx, item_idx]
                rate_prob = rating_probability * (1 + preference)
                
                if np.random.random() < rate_prob:
                    # 선호도를 1-5 평점으로 변환
                    rating = int(np.clip(preference * 5 + np.random.normal(0, 0.5), 1, 5))
                    
                    ratings.append({
                        'user_id': preference_matrix.index[user_idx],
                        'item_id': preference_matrix.columns[item_idx], 
                        'rating': rating,
                        'preference_score': preference
                    })
        
        return pd.DataFrame(ratings)
    
    def generate_psychology_test_results(self, user_ids: List[str]) -> pd.DataFrame:
        """사용자별 심리테스트 결과 생성"""
        
        results = []
        persona_names = list(self.personas.keys())
        
        for user_id in user_ids:
            # 사용자의 페르소나 결정
            persona_name = np.random.choice(persona_names)
            persona = self.personas[persona_name]
            
            # 심리테스트 점수 생성 (노이즈 추가)
            test_result = {'user_id': user_id, 'persona': persona_name}
            
            for trait, base_score in persona['traits'].items():
                # 개인차를 위한 노이즈 추가
                noise = np.random.normal(0, 0.1)
                score = np.clip(base_score + noise, 0, 1)
                test_result[trait] = score
            
            results.append(test_result)
        
        return pd.DataFrame(results)

def main():
    """사용 예시"""
    generator = PersonaGTGenerator()
    
    # 1. 사용자-아이템 선호도 매트릭스 생성
    preference_matrix = generator.generate_user_item_matrix(n_users=200, n_items=100)
    print("선호도 매트릭스 생성 완료:", preference_matrix.shape)
    
    # 2. 명시적 평점 데이터 생성  
    ratings_df = generator.generate_explicit_ratings(preference_matrix)
    print("평점 데이터 생성 완료:", len(ratings_df), "개 평점")
    
    # 3. 심리테스트 결과 생성
    user_ids = preference_matrix.index.tolist()
    psychology_df = generator.generate_psychology_test_results(user_ids)
    print("심리테스트 결과 생성 완료:", len(psychology_df), "명 사용자")
    
    # 4. 데이터 저장
    preference_matrix.to_csv("synthetic_preferences.csv")
    ratings_df.to_csv("synthetic_ratings.csv", index=False)
    psychology_df.to_csv("synthetic_psychology.csv", index=False)
    
    print("\n=== 생성된 데이터 샘플 ===")
    print("평점 데이터:")
    print(ratings_df.head())
    print("\n심리테스트 결과:")
    print(psychology_df.head())

if __name__ == "__main__":
    main()
