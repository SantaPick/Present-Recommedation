# 벡터 DB vs 그래프 DB 분석

## 🤔 벡터 DB 사용 여부 결정

### 우리 프로젝트의 특성
- **지식 그래프 기반**: User-Item-Trait-Concept 관계 구조
- **심리테스트 점수**: 연속형 수치 데이터 (0-1 범위)
- **상품 속성**: RGB 색상, 질감, 기능 등 다차원 특성

## 📊 접근법 비교

### 1. 순수 그래프 기반 (벡터 DB 없음)
```python
# 장점: 구조가 단순하고 해석 가능
def graph_only_recommendation(user_psychology, knowledge_graph):
    item_scores = {}
    
    for item in all_items:
        score = 0
        
        # 직접 경로: User → Trait → Item
        for trait, user_score in user_psychology.items():
            if knowledge_graph.has_edge(trait, item):
                trait_item_weight = knowledge_graph[trait][item]['weight']
                score += user_score * trait_item_weight
        
        # 간접 경로: User → Trait → Concept → Item  
        for trait, user_score in user_psychology.items():
            for concept in knowledge_graph.neighbors(trait):
                if knowledge_graph.has_edge(concept, item):
                    trait_concept_weight = knowledge_graph[trait][concept]['weight']
                    concept_item_weight = knowledge_graph[concept][item]['weight']
                    score += user_score * trait_concept_weight * concept_item_weight
        
        item_scores[item] = score
    
    return sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
```

**장점**:
- ✅ 해석 가능성 높음 (경로 추적 가능)
- ✅ 구현 단순함
- ✅ 도메인 지식 직접 반영 가능

**단점**:
- ❌ 복잡한 패턴 학습 어려움
- ❌ 대용량 데이터 처리 한계
- ❌ 유사도 기반 추천 불가

### 2. 벡터 DB 기반
```python
# 장점: 유사도 검색 및 대용량 처리
import faiss
import numpy as np

class VectorBasedRecommender:
    def __init__(self, embedding_dim=128):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(embedding_dim)  # 내적 기반 유사도
        self.item_embeddings = {}
        
    def create_embeddings(self, users, items, knowledge_graph):
        """그래프 구조를 임베딩으로 변환"""
        
        # Node2Vec 또는 GraphSAGE로 노드 임베딩 생성
        embeddings = self.learn_graph_embeddings(knowledge_graph)
        
        # 아이템 임베딩을 벡터 DB에 저장
        item_vectors = []
        for item in items:
            embedding = embeddings[item]
            item_vectors.append(embedding)
            self.item_embeddings[len(item_vectors)-1] = item
        
        # FAISS 인덱스에 추가
        item_matrix = np.array(item_vectors).astype('float32')
        self.index.add(item_matrix)
    
    def recommend(self, user_psychology, top_k=10):
        """사용자 심리 프로필 기반 추천"""
        
        # 사용자 벡터 생성 (심리테스트 점수 기반)
        user_vector = self.create_user_vector(user_psychology)
        
        # 벡터 유사도 검색
        scores, indices = self.index.search(
            user_vector.reshape(1, -1).astype('float32'), 
            top_k
        )
        
        # 결과 반환
        recommendations = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            item_id = self.item_embeddings[idx]
            recommendations.append((item_id, float(score)))
        
        return recommendations
```

**장점**:
- ✅ 대용량 데이터 고속 처리
- ✅ 복잡한 패턴 학습 가능
- ✅ 확장성 우수

**단점**:
- ❌ 블랙박스 (해석 어려움)
- ❌ 구현 복잡도 높음
- ❌ 임베딩 학습 필요

### 3. 하이브리드 접근법 (추천)
```python
class HybridKGRecommender:
    def __init__(self):
        self.graph_recommender = GraphOnlyRecommender()
        self.vector_recommender = VectorBasedRecommender()
        
    def recommend(self, user_psychology, top_k=10, alpha=0.7):
        """그래프 + 벡터 하이브리드 추천"""
        
        # 1. 그래프 기반 추천 (해석 가능)
        graph_scores = self.graph_recommender.recommend(user_psychology, top_k*2)
        
        # 2. 벡터 기반 추천 (성능 우수)  
        vector_scores = self.vector_recommender.recommend(user_psychology, top_k*2)
        
        # 3. 점수 결합
        combined_scores = {}
        
        # 그래프 점수 정규화
        max_graph_score = max([score for _, score in graph_scores]) if graph_scores else 1
        for item, score in graph_scores:
            combined_scores[item] = alpha * (score / max_graph_score)
        
        # 벡터 점수 추가
        max_vector_score = max([score for _, score in vector_scores]) if vector_scores else 1
        for item, score in vector_scores:
            if item in combined_scores:
                combined_scores[item] += (1-alpha) * (score / max_vector_score)
            else:
                combined_scores[item] = (1-alpha) * (score / max_vector_score)
        
        # 최종 순위
        final_recommendations = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return final_recommendations
    
    def explain_recommendation(self, user_id, item_id):
        """추천 이유 설명 (그래프 경로 기반)"""
        paths = self.graph_recommender.find_recommendation_paths(user_id, item_id)
        
        explanations = []
        for path in paths:
            explanation = f"당신의 {path[1]} 성향이 높아서 → {path[2]} 특성을 가진 → {item_id} 상품을 추천합니다"
            explanations.append(explanation)
        
        return explanations
```

## 🎯 우리 프로젝트 권장 사항

### Phase 1: 순수 그래프 기반 (프로토타입)
```python
# NetworkX로 시작
- 그래프 구조 검증
- 기본 추천 알고리즘 구현
- 해석 가능성 확보
- 도메인 전문가 검토
```

### Phase 2: 하이브리드 시스템 (실제 서비스)
```python
# 그래프 + 벡터 DB 결합
- FAISS 또는 Milvus 도입
- 그래프 임베딩 학습 (Node2Vec, GraphSAGE)
- 성능과 해석가능성 균형
- A/B 테스트로 효과 검증
```

## 🛠️ 기술 스택 추천

### 벡터 DB 옵션
| 도구 | 장점 | 단점 | 적합성 |
|------|------|------|--------|
| **FAISS** | 무료, 빠름, 로컬 사용 | 분산 처리 한계 | ⭐⭐⭐⭐⭐ |
| **Milvus** | 분산 처리, 확장성 | 설치 복잡 | ⭐⭐⭐⭐ |
| **Chroma** | 간단한 API, 오픈소스 | 상대적으로 신생 | ⭐⭐⭐ |
| **Pinecone** | 관리형 서비스 | 유료, 종속성 | ⭐⭐ |

### 그래프 임베딩 라이브러리
```python
# Node2Vec (간단함)
from node2vec import Node2Vec

# PyTorch Geometric (고성능)
from torch_geometric.nn import Node2Vec, GraphSAGE

# DGL (유연함)
import dgl
```

## 📋 구현 단계별 계획

### 1단계: 그래프 기반 프로토타입
- [ ] NetworkX로 지식그래프 구축
- [ ] 기본 경로 기반 추천 알고리즘
- [ ] 추천 이유 설명 기능
- [ ] 소규모 데이터로 검증

### 2단계: 벡터 임베딩 추가
- [ ] Node2Vec으로 그래프 임베딩 학습
- [ ] FAISS 벡터 인덱스 구축
- [ ] 유사도 기반 추천 구현
- [ ] 성능 비교 (그래프 vs 벡터)

### 3단계: 하이브리드 시스템
- [ ] 그래프 + 벡터 점수 결합
- [ ] 가중치 최적화 (alpha 튜닝)
- [ ] 실시간 추천 API 구현
- [ ] 대용량 데이터 처리 최적화

## 💡 결론

**벡터 DB 사용 권장**: 하지만 단계적 접근
1. **시작**: 순수 그래프 기반 (해석가능성 우선)
2. **발전**: 하이브리드 시스템 (성능 + 해석가능성)
3. **최적화**: 벡터 DB 활용한 대용량 처리

이렇게 하면 **도메인 지식의 명확성**과 **머신러닝의 성능** 둘 다 확보할 수 있습니다!
