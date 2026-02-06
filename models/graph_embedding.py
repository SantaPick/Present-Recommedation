"""
그래프 임베딩 모델 구현
Node2Vec 기반 그래프 임베딩 + 추천 시스템
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from node2vec import Node2Vec
import pickle
from pathlib import Path

class GraphEmbeddingModel:
    """그래프 임베딩 기반 추천 모델"""
    
    def __init__(self, config):
        self.config = config
        self.embedding_dim = config["embedding_dim"]
        self.graph = None
        self.node_embeddings = None
        self.node_to_idx = {}
        self.idx_to_node = {}
        
    def load_graph(self, graph_path):
        """그래프 데이터 로드"""
        with open(graph_path, 'rb') as f:
            graph_data = pickle.load(f)
        
        self.graph = graph_data['graph']
        self.node_types = graph_data['node_types']
        self.node_id_mapping = graph_data.get('node_id_mapping', {})
        
        # 노드 인덱스 매핑 생성
        all_nodes = list(self.graph.nodes())
        self.node_to_idx = {node: idx for idx, node in enumerate(all_nodes)}
        self.idx_to_node = {idx: node for idx, node in enumerate(all_nodes)}
        
        print(f"그래프 로드 완료: {len(all_nodes)}개 노드, {self.graph.number_of_edges()}개 엣지")
        
    def train_embeddings(self, dimensions=128, walk_length=30, num_walks=200, workers=4):
        """Node2Vec를 이용한 그래프 임베딩 학습"""
        print("Node2Vec 임베딩 학습 시작...")
        
        # Node2Vec 모델 생성
        node2vec = Node2Vec(
            self.graph,
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            workers=workers,
            p=1,  # Return parameter
            q=1   # In-out parameter
        )
        
        # 임베딩 학습
        model = node2vec.fit(
            window=10,
            min_count=1,
            batch_words=4,
            epochs=10
        )
        
        # 임베딩 추출
        embeddings = {}
        for node in self.graph.nodes():
            try:
                embeddings[node] = model.wv[str(node)]
            except KeyError:
                # 노드가 없는 경우 랜덤 임베딩
                embeddings[node] = np.random.normal(0, 0.1, dimensions)
        
        self.node_embeddings = embeddings
        print(f"임베딩 학습 완료: {len(embeddings)}개 노드")
        
        return embeddings
    
    
    
    def save_embeddings(self, save_path):
        """임베딩 저장"""
        embedding_data = {
            'embeddings': self.node_embeddings,
            'node_to_idx': self.node_to_idx,
            'idx_to_node': self.idx_to_node,
            'config': self.config
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(embedding_data, f)
        
        print(f"임베딩 저장 완료: {save_path}")
    
    def load_embeddings(self, load_path):
        """임베딩 로드"""
        with open(load_path, 'rb') as f:
            embedding_data = pickle.load(f)
        
        self.node_embeddings = embedding_data['embeddings']
        self.node_to_idx = embedding_data['node_to_idx']
        self.idx_to_node = embedding_data['idx_to_node']
        
        print(f"임베딩 로드 완료: {len(self.node_embeddings)}개 노드")


class SimpleGCN(nn.Module):
    """간단한 GCN 모델 (선택적 사용)"""
    
    def __init__(self, input_dim, hidden_dims, output_dim, dropout=0.2):
        super().__init__()
        
        layers = []
        dims = [input_dim] + hidden_dims + [output_dim]
        
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            if i < len(dims) - 2:  # 마지막 레이어가 아닌 경우
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(dropout))
        
        self.layers = nn.ModuleList(layers)
    
    def forward(self, x, adj_matrix):
        """순전파"""
        for i, layer in enumerate(self.layers):
            if isinstance(layer, nn.Linear):
                if i == 0:
                    x = torch.matmul(adj_matrix, x)
                x = layer(x)
            else:
                x = layer(x)
        
        return x