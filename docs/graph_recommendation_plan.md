# 그래프 기반 추천시스템 구현 계획

## 📋 프로젝트 개요
- **목표**: 심리테스트 기반 선물 추천 시스템
- **접근법**: 이종 그래프 신경망 (Heterogeneous Graph Neural Network)
- **노드 타입**: User, Item, Trait, Concept

## 🏗️ 그래프 구조 설계

### 노드 정의
1. **User 노드**: 사용자 (심리테스트 응답자)
2. **Item 노드**: 선물 상품 (products.csv의 각 상품)
3. **Trait 노드**: 심리적 특성 (Big-Five, CNFU, CVPA, MSV 요인들)
4. **Concept 노드**: 상품 컨셉 (LLM으로 추출할 10가지 개념)

### 엣지 정의
1. **User ↔ Trait**: 심리테스트 점수 기반 가중치
2. **User ↔ Concept**: 추가 질문을 통한 선호도
3. **Item ↔ Trait**: 상품의 심리적 특성 매핑
4. **Item ↔ Concept**: 상품이 가진 컨셉 특성
5. **Trait ↔ Concept**: 심리적 특성과 컨셉 간 연관성

## 🛠️ 기술 스택 선정

### 1단계: 프로토타입 (NetworkX)
- **목적**: 그래프 구조 검증 및 시각화
- **장점**: 빠른 개발, 직관적 API
- **사용 시점**: 초기 설계 및 데이터 탐색

### 2단계: 실제 구현 (PyTorch Geometric)
- **목적**: 실제 추천 모델 학습 및 서비스
- **장점**: GPU 가속, 최신 GNN 모델 지원
- **사용 시점**: 본격적인 모델 개발

## 📚 참고 모델

### LightGCN (추천)
```python
# 간단하고 효과적인 그래프 기반 협업 필터링
# User-Item 이분 그래프에서 시작하여 확장 가능
```

### HetGNN (고려)
```python
# 이종 그래프 처리에 특화
# User-Item-Trait-Concept 다중 노드 타입 처리 가능
```

## 🗂️ 모듈 구조

```
Present-Recommedation/
├── data/
│   ├── graph_builder.py      # 그래프 구축
│   ├── data_loader.py        # 데이터 로딩
│   └── preprocessor.py       # 전처리
├── models/
│   ├── lightgcn.py          # LightGCN 구현
│   ├── hetgnn.py            # HetGNN 구현
│   └── base_model.py        # 기본 모델 클래스
├── training/
│   ├── trainer.py           # 모델 학습
│   ├── evaluator.py         # 성능 평가
│   └── config.py            # 설정 관리
├── inference/
│   ├── recommender.py       # 추천 엔진
│   └── explainer.py         # 추천 이유 설명
├── utils/
│   ├── graph_utils.py       # 그래프 유틸리티
│   ├── metrics.py           # 평가 지표
│   └── visualization.py     # 시각화
└── notebooks/
    ├── data_exploration.ipynb
    ├── model_comparison.ipynb
    └── recommendation_demo.ipynb
```

## 🚀 구현 단계

### Phase 1: 데이터 준비 및 그래프 구축
1. 심리테스트 데이터 정제 (50-60 문항)
2. 상품-특성 매핑 데이터 생성
3. NetworkX로 그래프 구조 프로토타입

### Phase 2: 모델 개발
1. PyTorch Geometric 환경 구축
2. LightGCN 기본 모델 구현
3. 이종 그래프 확장 (HetGNN)

### Phase 3: 학습 및 평가
1. 학습 데이터셋 구성
2. 모델 학습 및 하이퍼파라미터 튜닝
3. 추천 성능 평가 (NDCG, Recall@K 등)

### Phase 4: 서비스 통합
1. 추천 API 개발
2. 실시간 추천 시스템 구축
3. 사용자 피드백 수집 및 모델 업데이트

## 📊 예상 데이터 플로우

```
사용자 심리테스트 응답
    ↓
그래프 임베딩 생성
    ↓
유사 사용자/상품 탐색
    ↓
추천 점수 계산
    ↓
Top-K 상품 추천
    ↓
추천 이유 설명 생성
```

## 🎯 성공 지표
- **정확도**: NDCG@10 > 0.3
- **다양성**: Intra-List Diversity > 0.7
- **설명가능성**: 추천 이유 제공 가능
- **확장성**: 10만 사용자, 1만 상품 처리 가능

## 📝 다음 단계
1. [ ] NetworkX 프로토타입 구현
2. [ ] 심리테스트-상품 매핑 데이터 생성
3. [ ] PyTorch Geometric 환경 구축
4. [ ] LightGCN 기본 모델 구현
5. [ ] 성능 평가 및 최적화
