# Graph Data Files

그래프 구축을 위한 노드 및 엣지 정의 파일들

## 파일 구성

### 노드 정의 파일

#### entity_list.txt
모든 노드의 ID 매핑 정보
- Trait 노드: 200번대 (심리적 특성)
- Concept 노드: 300번대 (상품 개념적 특성)  
- Item 노드: 1000번대부터 (상품, 동적 추가)
- User 노드: 2000번대부터 (사용자, 동적 추가)

### 엣지 가중치 파일 (TXT)

#### Trait_Concept_Weight.txt
Trait-Concept 간 관계 가중치
- 심리적 특성과 개념적 특성 간 상관관계
- 형식: `Trait노드ID Concept노드ID 가중치`
- 가중치 범위: 실수값 (양수/음수 가능)
- 생성: `Trait-Concept-Weight.xlsx.csv`에서 자동 생성

#### item_concept_weights.txt
Item-Concept 간 관계 가중치
- 상품과 개념적 특성 간 연결 정보
- 형식: `Item노드ID Concept노드ID 가중치`
- 가중치 범위: 0.0~1.0 (1-5 점수를 5로 나눈 정규화 값)
- 생성: `Item_Concepts_Weight.csv`에서 자동 생성

#### item_trait_weights.txt
Item-Trait 간 관계 가중치
- 상품과 심리적 특성 간 연결 정보
- 형식: `Item노드ID Trait노드ID 가중치`
- 가중치 범위: 실수값 (Big 5 성격 점수 등)
- 생성: `Item-Trait-Weight.csv`에서 자동 생성

### 원본 데이터 파일 (CSV)

#### Item_Concepts_Weight.csv
상품별 Concept 점수 원본 데이터
- 컬럼: product_id, name, description 등 상품 정보 + Concept 점수 (Unique, Calm, Simple 등)
- Concept 점수: 1~5 정수값
- 용도: `item_concept_weights.txt` 생성에 사용

#### Item-Trait-Weight.csv
상품별 Trait 점수 원본 데이터
- 컬럼: product_id, name, description, review_count 등 + Trait 점수 (Openness, Conscientiousness 등)
- Trait 점수: 실수값 (Big 5 성격 점수, 선호도 점수 등)
- 용도: `item_trait_weights.txt` 생성에 사용

#### Trait-Concept-Weight.xlsx.csv
Trait-Concept 간 상관관계 원본 데이터
- 컬럼: Trait (행) × Concept (열) 매트릭스 형태
- 가중치: 실수값 (상관계수 등)
- 용도: `Trait_Concept_Weight.txt` 생성에 사용

### 스크립트 파일

#### update_graph_weights.py
모든 가중치 TXT 파일을 자동 생성하는 스크립트
- CSV 파일들을 읽어서 `entity_list.txt`를 참조하여 TXT 파일 생성
- 기존 TXT 파일은 자동 삭제 후 신버전 생성
- entity_list.txt의 노드 정보를 동적으로 참조