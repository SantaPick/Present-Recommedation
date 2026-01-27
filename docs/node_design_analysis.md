# 노드 구조 설계 분석

## 🎯 최종 노드 구성 제안

### 1. User 노드
- **정의**: 심리테스트를 완료한 사용자
- **속성**: user_id, 심리테스트 완료 여부
- **개수**: 실제 사용자 수에 따라 가변

### 2. Item 노드  
- **정의**: products.csv의 선물 상품들
- **속성**: product_id, name, price, category
- **개수**: ~850개 (products.csv 기준)

### 3. Trait 노드 (13개)
- **Big-Five 요소 (5개)**:
  - extraversion (외향성)
  - agreeableness (친화성) 
  - conscientiousness (성실성)
  - emotional_stability (정서안정성)
  - openness (개방성)

- **CNFU 요소 (3개)**:
  - creative_choice (창의적 선택)
  - unpopular_choice (비인기 선택)
  - avoidance_similarity (유사성 회피)

- **CVPA 요소 (3개)**:
  - aesthetic_value (미적 가치)
  - aesthetic_acumen (미적 통찰력)
  - aesthetic_response (미적 반응)

- **MSV 요소 (2개)**:
  - materialism_centrality (물질주의 중심성)
  - materialism_happiness (물질주의 행복)

### 4. Concept 노드 (물리적/범주적 속성만)

#### 4.1 색상 계열 (5개) - RGB + 색온도
- red (R 채널)
- green (G 채널)  
- blue (B 채널)
- warm_color (따뜻한 색조)
- cool_color (차가운 색조)

#### 4.2 질감 계열 (3개)
- texture_soft (부드러운: 패브릭, 실크 등)
- texture_hard (단단한: 금속, 나무, 플라스틱)
- texture_smooth (매끄러운: 유리, 세라믹)

#### 4.3 기능 계열 (4개)
- functional (실용적 기능 중심)
- entertainment (오락/엔터테인먼트)
- relaxation (휴식/힐링)
- social (사회적/공유 목적)

#### 4.4 브랜드/인증 계열 (3개)
- premium_brand (고급 브랜드)
- eco_certified (환경 인증)
- handmade (수제/핸드메이드)

**총 Concept 노드: 13개**

## 🔗 엣지 구성

### 1. User ↔ Trait 엣지
- **가중치**: 심리테스트 점수 (정규화된 0-1 값)
- **방향**: 무방향 그래프
- **예시**: (user_1, extraversion, weight=0.8)

### 2. User ↔ Concept 엣지  
- **가중치**: 추가 선호도 질문 결과
- **방향**: 무방향 그래프
- **예시**: (user_1, color_warm, weight=0.7)

### 3. Item ↔ Trait 엣지
- **가중치**: 상품의 심리적 특성 점수
- **매핑 방법**: 
  - LLM 기반 상품 분석
  - 전문가 라벨링
  - 사용자 피드백 수집
- **예시**: (product_9971687, extraversion, weight=0.6)

### 4. Item ↔ Concept 엣지
- **가중치**: 상품이 해당 컨셉을 가지는 정도 (0-1)
- **매핑 방법**: 
  - **색상**: 이미지 RGB 분석 → 각 색상 노드별 가중치 계산
  - **질감**: 이미지 텍스처 분석 + 상품명 키워드
  - **기능/브랜드**: 상품 설명 텍스트 분석 + 카테고리 규칙
- **색상 예시**: 
  - 빨간 장미 → (item, red, weight=0.9), (item, warm_color, weight=0.8)
  - 파란 셔츠 → (item, blue, weight=0.8), (item, cool_color, weight=0.7)

### 5. Trait ↔ Concept 엣지
- **가중치**: 심리학 연구 기반 연관성
- **방향**: 무방향 그래프  
- **예시**: (openness, color_warm, weight=0.4)

## 📊 엣지 가중치로 처리할 속성들

다음 속성들은 **노드가 아닌 엣지 가중치**로 처리:

### 연속형 평가 척도 (1-5점)
- **uniqueness_score**: 흔한(1) ↔ 유니크한(5)
- **intensity_score**: 차분한(1) ↔ 강렬한(5)  
- **complexity_score**: 심플한(1) ↔ 복잡한(5)
- **value_type_score**: 물질적(1) ↔ 의미적(5)
- **saturation_score**: 낮은 채도(1) ↔ 높은 채도(5)

### 구현 방법
```python
# RGB 기반 색상 가중치 계산
def calculate_color_weights(rgb_values):
    r, g, b = [x/255.0 for x in rgb_values]  # 정규화
    
    # 색온도 계산 (따뜻함/차가움)
    warm_score = (r + max(0, r-g) + max(0, r-b)) / 3
    cool_score = (b + max(0, b-r) + max(0, g-r)) / 3
    
    return {
        'red': r,
        'green': g, 
        'blue': b,
        'warm_color': warm_score,
        'cool_color': cool_score
    }

# 예시
edge_data = {
    ('product_9971687', 'red'): {
        'base_weight': 0.8,      # R 채널 값
        'saturation_score': 3.5,  # 채도 (엣지 속성)
        'brightness': 0.6        # 밝기 (엣지 속성)
    },
    ('product_9971687', 'warm_color'): {
        'base_weight': 0.7,      # 따뜻한 색조 점수
        'intensity_score': 4.2   # 강렬함 (엣지 속성)
    }
}
```

## 🎯 장점

### 1. 명확한 역할 분리
- **노드**: 명확한 개체 (사용자, 상품, 특성, 컨셉)
- **엣지**: 관계의 강도 및 다차원 속성

### 2. 확장성
- 새로운 Concept 노드 추가 용이
- 새로운 평가 척도를 엣지 가중치로 추가 가능

### 3. 해석가능성  
- 각 노드의 의미가 명확
- 추천 결과 설명 시 직관적

## 🚧 구현 시 고려사항

### 1. 데이터 수집
- Item ↔ Trait 매핑 데이터 필요
- Item ↔ Concept 매핑 데이터 필요  
- Trait ↔ Concept 연관성 연구 자료 필요

### 2. 스케일링
- 사용자 수 증가에 따른 그래프 크기 관리
- 실시간 추천을 위한 효율적인 그래프 탐색

### 3. 콜드 스타트 문제
- 신규 사용자 처리 방안
- 신규 상품 처리 방안

## 📝 다음 단계

1. **데이터 매핑 작업**
   - products.csv → Item-Concept 매핑
   - 심리학 연구 → Trait-Concept 매핑

2. **프로토타입 구현**
   - NetworkX로 그래프 구조 검증
   - 샘플 데이터로 추천 알고리즘 테스트

3. **평가 지표 설정**
   - 추천 정확도 측정 방법
   - 사용자 만족도 평가 방법
