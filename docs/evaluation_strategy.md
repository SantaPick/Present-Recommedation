# 추천시스템 평가 전략

## 🎯 평가의 핵심 과제
- **GT 부재**: 명확한 정답이 없는 추천 도메인
- **주관성**: 개인 취향의 다양성
- **상황 의존성**: 맥락에 따른 선호도 변화

## 📊 다층 평가 프레임워크

### 1단계: 오프라인 평가 (Synthetic GT)

#### 1.1 심리-상품 매칭 정확도
```python
# 전문가 라벨링 기반 GT 생성
expert_labels = {
    "high_extraversion_users": ["파티용품", "소셜게임", "공유음식"],
    "high_openness_users": ["예술품", "독특한디자인", "새로운경험"],
    "high_conscientiousness_users": ["실용용품", "정리도구", "플래너"]
}

# 평가 지표
def calculate_matching_accuracy():
    return {
        "trait_item_alignment": "심리특성-상품 매칭 정확도",
        "concept_relevance": "컨셉 연관성 점수",
        "category_distribution": "추천 카테고리 다양성"
    }
```

#### 1.2 Cross-Validation 기반 평가
```python
# 기존 사용자 데이터 분할
def cross_validation_evaluation():
    # 80% 학습, 20% 테스트로 분할
    # 테스트 사용자의 심리테스트 → 추천 생성
    # 실제 선호 상품과 비교 (있는 경우)
    
    metrics = {
        "precision_at_k": "상위 K개 추천 정확도",
        "recall_at_k": "실제 선호 상품 포함률", 
        "ndcg": "순위 기반 정확도",
        "diversity": "추천 다양성",
        "novelty": "새로운 상품 발견률"
    }
    return metrics
```

### 2단계: 온라인 평가 (실제 사용자)

#### 2.1 A/B 테스트 설계
```python
test_design = {
    "control_group": {
        "method": "인기도 기반 추천",
        "size": "전체 사용자의 50%"
    },
    "treatment_group": {
        "method": "그래프 기반 심리테스트 추천", 
        "size": "전체 사용자의 50%"
    },
    "duration": "4주간",
    "metrics": [
        "click_through_rate",
        "conversion_rate", 
        "user_satisfaction_score",
        "return_visit_rate"
    ]
}
```

#### 2.2 암시적 피드백 수집
```python
implicit_feedback = {
    "behavioral_signals": {
        "click": 1,           # 상품 클릭
        "view_time": "초단위",  # 상품 페이지 체류시간
        "add_cart": 3,        # 장바구니 추가
        "purchase": 5,        # 실제 구매
        "share": 2,           # 공유하기
        "wishlist": 2         # 위시리스트 추가
    },
    "negative_signals": {
        "quick_bounce": -1,   # 빠른 이탈
        "skip": -0.5,         # 추천 건너뛰기
        "hide": -2            # 추천 숨기기
    }
}
```

### 3단계: 정성적 평가

#### 3.1 사용자 인터뷰
```python
interview_protocol = {
    "participants": "20-30명 (다양한 심리 프로필)",
    "duration": "30분",
    "questions": [
        "추천받은 상품이 본인 취향과 얼마나 맞나요?",
        "추천 이유가 납득되나요?",
        "실제로 구매하고 싶은 상품이 있나요?",
        "기존 추천과 비교해 어떤가요?"
    ],
    "metrics": [
        "relevance_score (1-5)",
        "explainability_score (1-5)", 
        "purchase_intention (1-5)",
        "overall_satisfaction (1-5)"
    ]
}
```

#### 3.2 전문가 평가
```python
expert_evaluation = {
    "evaluators": "심리학자 + 마케팅 전문가 + UX 디자이너",
    "criteria": [
        "심리학적 타당성",
        "상품 매칭의 논리성",
        "추천 설명의 설득력",
        "사용자 경험 품질"
    ],
    "method": "블라인드 평가 (알고리즘 정보 미제공)"
}
```

## 🎯 핵심 평가 지표

### 정량적 지표
```python
quantitative_metrics = {
    # 정확도 관련
    "precision_at_10": "상위 10개 추천 중 관련 상품 비율",
    "recall_at_10": "사용자가 좋아할 상품 중 추천된 비율",
    "ndcg_at_10": "순위를 고려한 정확도",
    
    # 다양성 관련  
    "intra_list_diversity": "추천 목록 내 다양성",
    "coverage": "전체 상품 중 추천되는 비율",
    "novelty": "인기도가 낮은 상품 추천 비율",
    
    # 비즈니스 관련
    "click_through_rate": "추천 클릭률",
    "conversion_rate": "구매 전환율",
    "revenue_per_user": "사용자당 매출"
}
```

### 정성적 지표
```python
qualitative_metrics = {
    "user_satisfaction": "사용자 만족도 (설문)",
    "trust_score": "추천에 대한 신뢰도",
    "explainability": "추천 이유의 이해도",
    "serendipity": "예상치 못한 좋은 발견",
    "fairness": "다양한 사용자 그룹에 대한 공정성"
}
```

## 🚀 단계별 구현 계획

### Phase 1: 기본 평가 시스템 구축
```python
# 1. 심리테스트-상품 매칭 데이터셋 구축
# 2. 전문가 라벨링으로 소규모 GT 생성  
# 3. 기본 정량 지표 구현 (Precision, Recall, NDCG)
```

### Phase 2: 사용자 피드백 시스템
```python
# 1. 암시적 피드백 수집 시스템 구축
# 2. A/B 테스트 프레임워크 구현
# 3. 실시간 성능 모니터링 대시보드
```

### Phase 3: 고도화된 평가
```python
# 1. 사용자 인터뷰 및 정성 평가
# 2. 장기적 사용자 만족도 추적
# 3. 추천 설명 품질 평가
```

## 💡 GT 대안 전략

### 1. 합성 GT 생성
```python
def generate_synthetic_gt():
    """심리학 이론 기반 합성 정답 생성"""
    rules = {
        "high_extraversion": {
            "preferred_categories": ["파티용품", "소셜게임"],
            "avoid_categories": ["독서용품", "개인취미"]
        },
        "high_openness": {
            "preferred_attributes": ["unique", "artistic", "creative"],
            "avoid_attributes": ["conventional", "traditional"]
        }
    }
    return synthetic_labels
```

### 2. 상대적 평가
```python
def relative_evaluation():
    """절대 평가 대신 상대적 비교"""
    baselines = [
        "random_recommendation",
        "popularity_based", 
        "category_based",
        "collaborative_filtering"
    ]
    # 우리 모델 vs 베이스라인들 성능 비교
```

### 3. 점진적 학습
```python
def incremental_learning():
    """사용자 피드백으로 지속적 개선"""
    feedback_loop = {
        "collect_feedback": "사용자 행동 데이터 수집",
        "update_model": "모델 파라미터 업데이트", 
        "evaluate_improvement": "성능 개선 측정",
        "deploy_update": "개선된 모델 배포"
    }
```

## 📋 평가 체크리스트

- [ ] 전문가 라벨링으로 소규모 GT 구축 (100-200개 샘플)
- [ ] 기본 정량 지표 구현 (Precision@K, NDCG@K)
- [ ] A/B 테스트 프레임워크 설계
- [ ] 사용자 피드백 수집 시스템 구현
- [ ] 베이스라인 모델들과 성능 비교
- [ ] 사용자 인터뷰 프로토콜 설계
- [ ] 실시간 성능 모니터링 대시보드 구축
