"""
그래프 기반 추천시스템을 위한 지식 그래프 생성
txt 파일들을 기반으로 User-Item-Trait-Concept 그래프 구축
"""

import pandas as pd
import numpy as np
import networkx as nx
import pickle
import os

class GraphGenerator:
    def __init__(self):
        self.graph = nx.Graph()
        self.node_types = {
            'item': [],
            'trait': [],
            'concept': []
        }
        self.node_id_mapping = {}
        
    def load_entity_mappings(self, entity_file="./graph_data/entity_list.txt"):
        """entity_list.txt에서 노드 ID 매핑 로드"""
        self.node_id_mapping = {}
        
        with open(entity_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 3:
                        node_name, node_id, node_type = parts[0], int(parts[1]), parts[2]
                        self.node_id_mapping[node_name] = {
                            'id': node_id,
                            'type': node_type
                        }
        
        print(f"로드된 노드: {len(self.node_id_mapping)}개")
        
    def create_nodes_from_entities(self):
        """entity_list.txt 기반으로 모든 노드 생성"""
        for node_name, node_info in self.node_id_mapping.items():
            node_id = node_info['id']
            node_type = node_info['type']
            
            # 노드 생성
            self.graph.add_node(node_id, 
                              name=node_name, 
                              type=node_type,
                              original_id=node_name)
            
            # 노드 타입별 분류
            self.node_types[node_type].append(node_id)
        
        print("노드 생성 완료:")
        for node_type, nodes in self.node_types.items():
            print(f"  {node_type}: {len(nodes)}개")
    
    def load_trait_concept_edges(self, weights_file="graph_data/trait_concept_weights.txt"):
        """Trait-Concept 엣지 로드"""
        edge_count = 0
        
        with open(weights_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 3:
                        trait_id, concept_id, weight = int(parts[0]), int(parts[1]), float(parts[2])
                        
                        if trait_id in self.graph.nodes() and concept_id in self.graph.nodes():
                            self.graph.add_edge(trait_id, concept_id,
                                              relation='trait_concept',
                                              weight=weight)
                            edge_count += 1
        
        print(f"Trait-Concept 엣지 생성: {edge_count}개")
    
    def load_item_concept_edges(self, weights_file="./graph_data/item_concept_weights.txt"):
        """Item-Concept 엣지 로드"""
        edge_count = 0
        
        with open(weights_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 3:
                        item_id, concept_id, weight = int(parts[0]), int(parts[1]), float(parts[2])
                        
                        if item_id in self.graph.nodes() and concept_id in self.graph.nodes():
                            self.graph.add_edge(item_id, concept_id,
                                              relation='item_concept',
                                              weight=weight)
                            edge_count += 1
        
        print(f"Item-Concept 엣지 생성: {edge_count}개")
    
    def load_item_trait_edges(self, weights_file="./graph_data/item_trait_weights.txt"):
        """Item-Trait 엣지 로드 (가중치 -3~3을 -1~1로 스케일링)"""
        if not os.path.exists(weights_file) or os.path.getsize(weights_file) == 0:
            print("Item-Trait 엣지: 보류 상태 (파일 없음 또는 빈 파일)")
            return
        
        edge_count = 0
        with open(weights_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 3:
                        item_id, trait_id, weight = int(parts[0]), int(parts[1]), float(parts[2])
                        
                        if item_id in self.graph.nodes() and trait_id in self.graph.nodes():
                            # 가중치 -3~3 범위를 -1~1로 스케일링
                            scaled_weight = weight / 3.0
                            self.graph.add_edge(item_id, trait_id,
                                              relation='item_trait',
                                              weight=scaled_weight)
                            edge_count += 1
        
        print(f"Item-Trait 엣지 생성: {edge_count}개 (가중치 -3~3 → -1~1 스케일링 적용)")
    
    
    def build_base_graph(self):
        """기본 지식 그래프 구축 (User 노드 제외)"""
        print("=== 기본 그래프 구축 시작 ===")
        
        # 1. 노드 ID 매핑 로드
        self.load_entity_mappings()
        
        # 2. 모든 노드 생성
        self.create_nodes_from_entities()
        
        # 3. 엣지 생성
        self.load_trait_concept_edges()
        self.load_item_concept_edges()
        self.load_item_trait_edges()
        
        print("=== 기본 그래프 구축 완료 ===")
        self.print_graph_info()
        
        return self.graph
    
    def print_graph_info(self):
        """그래프 정보 출력"""
        print(f"\n그래프 정보:")
        print(f"  전체 노드: {self.graph.number_of_nodes()}개")
        print(f"  전체 엣지: {self.graph.number_of_edges()}개")
        
        print(f"\n노드 타입별:")
        for node_type, nodes in self.node_types.items():
            print(f"  {node_type}: {len(nodes)}개")
        
        # 엣지 타입별 통계
        edge_types = {}
        for _, _, data in self.graph.edges(data=True):
            relation = data.get('relation', 'unknown')
            edge_types[relation] = edge_types.get(relation, 0) + 1
        
        print(f"\n엣지 타입별:")
        for relation, count in edge_types.items():
            print(f"  {relation}: {count}개")
    
    def save_graph(self, save_path="./recommendation_graph.pkl"):
        """그래프를 pkl 파일로 저장"""
        graph_data = {
            'graph': self.graph,
            'node_types': self.node_types,
            'node_id_mapping': self.node_id_mapping
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(graph_data, f)
        
        print(f"\n그래프 저장 완료: {save_path}")
    
    def load_graph(self, load_path="./recommendation_graph.pkl"):
        """pkl 파일에서 그래프 로드"""
        with open(load_path, 'rb') as f:
            graph_data = pickle.load(f)
        
        self.graph = graph_data['graph']
        self.node_types = graph_data['node_types']
        self.node_id_mapping = graph_data['node_id_mapping']
        
        print(f"그래프 로드 완료: {load_path}")
        self.print_graph_info()

def main():
    """메인 실행 함수"""
    graph_gen = GraphGenerator()
    
    # 기본 그래프 구축 (User 노드 제외)
    graph = graph_gen.build_base_graph()
    
    # 그래프 저장
    graph_gen.save_graph("./recommendation_graph.pkl")

if __name__ == "__main__":
    main()