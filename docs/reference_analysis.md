# 지식 그래프 추천시스템 레퍼런스 분석

## 🎯 선정된 주요 레퍼런스

### 1. KGAT (Knowledge Graph Attention Network)
- **GitHub**: https://github.com/xiangwang1223/knowledge_graph_attention_network
- **논문**: KGAT: Knowledge Graph Attention Network for Recommendation (KDD 2019)
- **핵심 아이디어**: User-Item 상호작용 + Knowledge Graph를 GNN으로 통합 모델링

#### 코드 구조 분석
```python
# KGAT 핵심 구조
class KGAT(nn.Module):
    def __init__(self, n_users, n_items, n_entities, n_relations):
        # User, Item, Entity(Trait/Concept) 임베딩
        self.user_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_embedding = nn.Embedding(n_items, embedding_dim) 
        self.entity_embedding = nn.Embedding(n_entities, embedding_dim)
        
        # Attention 기반 메시지 전달
        self.attention_layers = nn.ModuleList([
            AttentionLayer(embedding_dim) for _ in range(n_layers)
        ])
    
    def forward(self, users, items):
        # 1. 초기 임베딩
        user_emb = self.user_embedding(users)
        item_emb = self.item_embedding(items)
        
        # 2. 그래프 어텐션으로 임베딩 업데이트
        for layer in self.attention_layers:
            user_emb, item_emb = layer(user_emb, item_emb, kg_graph)
        
        # 3. 추천 점수 계산
        scores = torch.sum(user_emb * item_emb, dim=1)
        return scores
```

#### 우리 프로젝트 적용 방안
```python
# SantaPick 적용 구조
nodes = {
    "users": ["user_1", "user_2", ...],
    "items": ["product_9971687", ...],  # products.csv
    "traits": ["extraversion", "openness", ...],  # 심리 특성
    "concepts": ["red", "warm_color", "social", ...]  # 상품 컨셉
}

edges = {
    "user_trait": [(user_id, trait_id, psychology_score)],
    "item_trait": [(item_id, trait_id, compatibility_score)], 
    "item_concept": [(item_id, concept_id, attribute_score)],
    "trait_concept": [(trait_id, concept_id, correlation_score)]
}
```

### 2. KG-Enhanced-Recommender
- **GitHub**: https://github.com/kaankvrck/KG-Enhanced-Recommender
- **특징**: Neo4j 그래프 DB + Cypher 쿼리 기반 추천

#### 핵심 구조
```python
# Neo4j 기반 지식 그래프 구축
class KGRecommender:
    def __init__(self, neo4j_uri, user, password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
    
    def create_knowledge_graph(self, users, items, relationships):
        # 노드 생성
        for user in users:
            self.create_user_node(user)
        for item in items:
            self.create_item_node(item)
        
        # 관계 생성
        for rel in relationships:
            self.create_relationship(rel)
    
    def recommend_items(self, user_id, top_k=10):
        # Cypher 쿼리로 추천
        query = """
        MATCH (u:User {id: $user_id})-[r1:HAS_TRAIT]->(t:Trait)
        MATCH (t)-[r2:COMPATIBLE_WITH]->(i:Item)
        RETURN i, SUM(r1.score * r2.score) as recommendation_score
        ORDER BY recommendation_score DESC
        LIMIT $top_k
        """
        return self.execute_query(query, user_id=user_id, top_k=top_k)
```

#### 장점
- 실제 그래프 DB 사용으로 확장성 좋음
- Cypher 쿼리로 복잡한 관계 탐색 가능
- 실시간 추천 서비스에 적합

### 3. OpenISS/kg-recommendation-framework  
- **GitHub**: https://github.com/OpenISS/kg-recommendation-framework
- **특징**: 모듈화된 KG 추천 프레임워크

#### 프로젝트 구조
```
kg-recommendation-framework/
├── data/
│   ├── preprocess.py          # 데이터 전처리
│   └── kg_builder.py          # 지식그래프 구축
├── models/
│   ├── base_model.py          # 기본 추천 모델
│   ├── kg_enhanced_model.py   # KG 강화 모델
│   └── evaluation.py          # 성능 평가
├── utils/
│   ├── metrics.py             # 평가 지표
│   └── visualization.py       # 시각화
└── experiments/
    └── run_experiments.py     # 실험 실행
```

## 🚀 구현 계획

### Phase 1: 프로토타입 (NetworkX 기반)
```python
# 1. 간단한 그래프 구조 검증
import networkx as nx

# 그래프 생성
G = nx.MultiDiGraph()

# 노드 추가
G.add_nodes_from(users, bipartite=0, node_type='user')
G.add_nodes_from(items, bipartite=1, node_type='item') 
G.add_nodes_from(traits, node_type='trait')
G.add_nodes_from(concepts, node_type='concept')

# 엣지 추가 (가중치 포함)
G.add_weighted_edges_from(user_trait_edges)
G.add_weighted_edges_from(item_trait_edges)
G.add_weighted_edges_from(item_concept_edges)

# 2. 기본 추천 알고리즘
def recommend_by_graph_walk(user_id, graph, top_k=10):
    """그래프 워크 기반 추천"""
    item_scores = {}
    
    # User → Trait → Item 경로
    for trait in graph.neighbors(user_id):
        if graph.nodes[trait]['node_type'] == 'trait':
            user_trait_weight = graph[user_id][trait]['weight']
            
            for item in graph.neighbors(trait):
                if graph.nodes[item]['node_type'] == 'item':
                    trait_item_weight = graph[trait][item]['weight']
                    score = user_trait_weight * trait_item_weight
                    item_scores[item] = item_scores.get(item, 0) + score
    
    # Top-K 반환
    return sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

### Phase 2: PyTorch Geometric 구현
```python
# KGAT 스타일 GNN 구현
import torch
import torch.nn as nn
from torch_geometric.nn import MessagePassing

class KGATLayer(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='add')
        self.lin = nn.Linear(in_channels, out_channels)
        self.attention = nn.MultiheadAttention(out_channels, num_heads=8)
    
    def forward(self, x, edge_index, edge_attr):
        # 메시지 전달 + 어텐션
        return self.propagate(edge_index, x=x, edge_attr=edge_attr)
    
    def message(self, x_j, edge_attr):
        # 어텐션 가중치 적용
        return self.attention(x_j, x_j, x_j)[0] * edge_attr.unsqueeze(-1)

class SantaPickKGAT(nn.Module):
    def __init__(self, n_users, n_items, n_traits, n_concepts, embedding_dim=64):
        super().__init__()
        
        # 임베딩 레이어
        total_nodes = n_users + n_items + n_traits + n_concepts
        self.node_embedding = nn.Embedding(total_nodes, embedding_dim)
        
        # KGAT 레이어들
        self.kgat_layers = nn.ModuleList([
            KGATLayer(embedding_dim, embedding_dim) for _ in range(3)
        ])
        
        # 예측 레이어
        self.predictor = nn.Linear(embedding_dim * 2, 1)
    
    def forward(self, user_ids, item_ids, edge_index, edge_attr):
        # 1. 초기 노드 임베딩
        x = self.node_embedding(torch.arange(self.node_embedding.num_embeddings))
        
        # 2. KGAT 레이어들 통과
        for layer in self.kgat_layers:
            x = layer(x, edge_index, edge_attr)
        
        # 3. 사용자-아이템 임베딩 추출
        user_emb = x[user_ids]
        item_emb = x[item_ids] 
        
        # 4. 추천 점수 예측
        concat_emb = torch.cat([user_emb, item_emb], dim=1)
        scores = self.predictor(concat_emb)
        
        return scores.squeeze()
```

### Phase 3: 평가 및 최적화
```python
# 평가 지표 구현
def evaluate_recommendations(model, test_data, top_k=10):
    metrics = {}
    
    # Precision@K, Recall@K
    precisions, recalls = [], []
    for user_id, true_items in test_data.items():
        recommended_items = model.recommend(user_id, top_k)
        
        relevant_items = set(true_items) & set(recommended_items)
        precision = len(relevant_items) / len(recommended_items)
        recall = len(relevant_items) / len(true_items)
        
        precisions.append(precision)
        recalls.append(recall)
    
    metrics['precision_at_k'] = np.mean(precisions)
    metrics['recall_at_k'] = np.mean(recalls)
    
    # NDCG@K
    ndcg_scores = []
    for user_id, true_items in test_data.items():
        recommended_items = model.recommend(user_id, top_k)
        ndcg = calculate_ndcg(true_items, recommended_items, top_k)
        ndcg_scores.append(ndcg)
    
    metrics['ndcg_at_k'] = np.mean(ndcg_scores)
    
    return metrics
```

## 📋 다음 단계

1. **KGAT 코드 분석 및 PyTorch 포팅**
2. **SantaPick 데이터에 맞는 그래프 스키마 설계**  
3. **NetworkX 프로토타입 구현**
4. **PyTorch Geometric 기반 실제 모델 구현**
5. **평가 시스템 구축 및 성능 측정**

## 🔗 참고 링크

- [KGAT GitHub](https://github.com/xiangwang1223/knowledge_graph_attention_network)
- [KG-Enhanced-Recommender](https://github.com/kaankvrck/KG-Enhanced-Recommender)  
- [OpenISS Framework](https://github.com/OpenISS/kg-recommendation-framework)
- [PyTorch Geometric 문서](https://pytorch-geometric.readthedocs.io/)
