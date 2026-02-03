# Graph Data Files

그래프 구축을 위한 노드 및 엣지 정의 파일들

## 파일 구성

### entity_list.txt
모든 노드의 ID 매핑 정보
- Trait 노드: 200번대 (심리적 특성)
- Concept 노드: 300번대 (상품 개념적 특성)  
- Item 노드: 1000번대부터 (상품, 동적 추가)
- User 노드: 2000번대부터 (사용자, 동적 추가)

### trait_concept_weights.txt
Trait-Concept 간 관계 가중치
- 심리적 특성과 개념적 특성 간 상관관계
- 가중치: +1 (양의 관계), -1 (음의 관계)

### item_concept_weights.txt
Item-Concept 간 관계 가중치
- 상품과 개념적 특성 간 연결 정보
- products_with_concepts.csv에서 자동 생성
- 가중치: 0.0~1.0 (1-5 점수를 정규화)

### item_trait_weights.txt
Item-Trait 간 관계 가중치
- 현재 보류 상태 (상품 의인화 작업 대기 중)

### generate_item_concept_weights.py
item_concept_weights.txt 파일 생성 스크립트
- CSV 파일에서 concept 점수를 읽어와 가중치 파일 생성