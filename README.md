# SantaPick - Present Recommendation System



## 프로젝트 구조

```
Present-Recommedation/
├── data/                           # 데이터 관련 폴더
│   ├── graph_data/                 # 그래프 구성 데이터
│   │   ├── entity_list.txt         # 노드 정보 (trait, concept, item)
│   │   ├── item_concept_weights.txt # Item-Concept 엣지 가중치
│   │   ├── item_trait_weights.txt  # Item-Trait 엣지 가중치
│   │   ├── Trait_Concept_Weight.txt # Trait-Concept 엣지 가중치
│   │   ├── Item_Concepts_Weight.csv # Item-Concept 원본 데이터
│   │   ├── Item-Trait-Weight.csv   # Item-Trait 원본 데이터
│   │   └── Trait-Concept-Weight.xlsx.csv # Trait-Concept 원본 데이터
│   ├── product/                    # 상품 관련 데이터
│   │   ├── images/                 # 상품 이미지
│   │   ├── products.csv            # 상품 정보
│   │   └── prompts/                # LLM 프롬프트
│   ├── psychology-question/        # 심리테스트 질문 데이터
│   │   ├── trait-question.csv      # 성격 특성 질문
│   │   ├── concept-question.csv    # 제품 선호도 질문
│   │   ├── 2-choice-question.csv   # 2지선다 질문
│   │   ├── 4-choice-question.csv   # 4지선다 질문
│   │   ├── 5-point-question.csv    # 5점 척도 질문
│   │   ├── O-X-question.csv        # O-X 질문
│   │   └── emotion-concept-relation.csv # 감정-개념 관계
│   ├── graph_gen.py                # 그래프 생성기
│   ├── graph_visualization.py      # 3D 그래프 시각화
│   └── recommendation_graph.pkl    # 학습된 그래프 데이터
├── models/                         # 모델 관련 폴더
│   ├── graph_embedding.py          # Node2Vec 그래프 임베딩
│   ├── trainer.py                  # 모델 학습 관리자
│   └── embeddings.pkl              # 학습된 임베딩 데이터
├── recommend/                      # 추천 시스템 폴더
│   ├── data_loader.py              # 심리테스트 데이터 로더
│   ├── scoring_calculator.py       # 가중치 계산기
│   ├── recommendation_engine.py    # 추천 엔진
│   └── psychology_scoring_rules.md # 가중치 계산 규칙
├── utils/                          # 유틸리티 폴더
│   └── config.py                   # 설정 파일
├── recommend_test.py               # Streamlit 웹 애플리케이션
├── pyproject.toml                  # 프로젝트 설정
├── requirements.txt                # 의존성 목록
└── README.md                       # 프로젝트 설명
```

## 폴더별 상세 설명

### data 폴더
그래프 구성과 상품 정보, 심리테스트 질문 데이터를 포함합니다.

- **graph_data/**: 지식 그래프 구성을 위한 노드와 엣지 정보
- **product/**: 상품 정보와 이미지, LLM 프롬프트
- **psychology-question/**: 심리테스트를 위한 다양한 질문 유형과 관계 데이터
- **graph_gen.py**: Trait-Concept-Item 기본 지식 그래프 생성
- **graph_visualization.py**: 3D 인터랙티브 그래프 시각화 (자동 회전 기능 포함)

### models 폴더
그래프 임베딩 모델 학습과 관련된 코드입니다.

- **graph_embedding.py**: Node2Vec을 사용한 그래프 임베딩 모델
- **trainer.py**: 기본 지식 그래프(Trait-Concept-Item) 학습 관리
- **embeddings.pkl**: 학습된 노드 임베딩 데이터

### recommend 폴더
사용자별 추천 시스템 구현 코드입니다.

- **data_loader.py**: 심리테스트 질문 데이터 로딩
- **scoring_calculator.py**: 사용자 응답 기반 가중치 계산
- **recommendation_engine.py**: 동적 User 노드 추가 및 추천 생성
- **psychology_scoring_rules.md**: 질문 유형별 가중치 계산 규칙

### recommend_test.py
Streamlit 기반 웹 애플리케이션으로, 심리테스트 진행과 추천 결과를 제공합니다.

- 성격 특성 및 제품 선호도 질문 진행
- 실시간 가중치 계산 및 시각화
- 상위 10개 맞춤형 상품 추천
- 추천 근거 및 상품 상세 정보 제공


## 환경 설정 및 실행 방법

### 방법 1: Conda 환경 사용

```bash
# 1. Conda 환경 생성 및 활성화
conda create -n santapick_ml python=3.10
conda activate santapick

# 2. 의존성 설치
pip install -r requirements.txt
# or
pip install -e .

# 3. 웹 애플리케이션 실행
streamlit run recommend_test.py
```

### 방법 2: Python venv 사용

```bash
# 1. 가상환경 생성
python -m venv santapick_env

# 2. 가상환경 활성화
# Linux/Mac:
source santapick_env/bin/activate
# Windows:
# santapick_env\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt
# or
pip install -e .

# 4. 웹 애플리케이션 실행
streamlit run recommend_test.py
```