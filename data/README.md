# Data Directory

이 폴더는 추천 시스템을 위한 데이터와 그래프 생성/시각화 관련 파일들을 포함합니다.

## 폴더 구조

### 📁 `graph_data/`
그래프 구축을 위한 기본 데이터 파일들
- 노드 정의 및 엣지 가중치 파일
- 자세한 내용은 `graph_data/README.md` 참조

### 📁 `product/`
상품 관련 원본 데이터
- `products_with_concepts.csv`: 상품-컨셉트 매핑 데이터

## 파일 설명

### 그래프 생성
- `graph_gen.py`: 지식 그래프 생성 스크립트
- `recommendation_graph.pkl`: 생성된 그래프 데이터 (pickle 형식)

### 시각화
- `graph_visualization.py`: 3D 인터랙티브 시각화 도구
- `knowledge_graph_3d.html`: 3D 시각화 결과 파일
- `knowledge_graph.gexf`: Gephi용 그래프 파일

## 사용 방법

### 1. 그래프 생성
```bash
python graph_gen.py
```

### 2. 시각화
```bash
python graph_visualization.py
```

생성된 `knowledge_graph_3d.html` 파일을 브라우저에서 열어 3D 인터랙티브 그래프를 확인할 수 있습니다.
