# 그래프 기반 추천시스템 구현 전략

## 📋 개발 순서

### Phase 1: 그래프 구축
- [ ] 데이터 로딩 및 전처리
- [ ] User-Item-Trait-Concept 그래프 생성
- [ ] 엣지 가중치 계산 로직
- [ ] 그래프 검증 및 시각화

### Phase 2: 모델 구현
- [ ] 베이스 모델 클래스 설계
- [ ] KGAT 모델 구현
- [ ] GraphSAGE 모델 구현
- [ ] LightGCN 모델 구현 (선택)

### Phase 3: 학습 파이프라인
- [ ] 자기지도학습 로직
- [ ] 평가 메트릭 구현
- [ ] 하이퍼파라미터 튜닝

### Phase 4: 추천 엔진
- [ ] 학습된 모델 로딩
- [ ] 실시간 추천 API
- [ ] 결과 후처리

## 🎯 현재 우선순위

**1단계: 그래프 구축부터 시작**
- data/graph.py 구현
- 실제 데이터로 그래프 생성 테스트
- 노드/엣지 구조 검증

**모델 구현은 그래프 완성 후 진행**

## 📁 폴더 구조

```
Present-Recommedation/
├── data/                  # 데이터 & 그래프
│   ├── loader.py         # CSV 데이터 로드
│   ├── graph.py          # 그래프 생성 & 관리
│   └── preprocessor.py   # 전처리
├── models/               # 모델 전체
│   ├── kgat.py          # KGAT 모델
│   ├── graphsage.py     # GraphSAGE 모델  
│   ├── trainer.py       # 학습 로직
│   ├── evaluator.py     # 평가
│   └── checkpoints/     # 저장된 모델들
├── recommend/            # 추천 실행
│   └── engine.py        # 추천 엔진
└── utils/               # 공통 유틸
    ├── config.py        # 설정
    └── logger.py        # 로깅
```

## 🔄 워크플로우

1. **그래프 생성**: `data/graph.py`에서 지식 그래프 구축
2. **모델 학습**: `models/trainer.py`로 자기지도학습
3. **추천 실행**: `recommend/engine.py`로 실시간 추천

## 📝 참고사항

- GT 없이 자기지도학습 방식 사용
- 여러 모델 후보군 실험 후 최적 모델 선택
- 그래프 구조 검증이 최우선 과제
