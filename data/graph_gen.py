"""
그래프 기반 추천시스템을 위한 지식 그래프 생성
User-Item-Trait-Concept 노드와 엣지를 구성
"""

import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict
import pickle
import os

class GraphGenerator:
    def __init__(self):
        self.graph = nx.Graph()
        self.node_types = {
            'user': [],
            'item': [],
            'trait': [],
            'concept': []
        }
        self.node_id_mapping = {}
        self.current_node_id = 1000  # User 노드용 시작 ID
        
        # 초기화 시 entity_list.txt에서 ID 매핑 로드
        self.load_entity_mappings()
        self.load_scale_trait_mapping()
        self.load_relation_mappings()
    
    def load_entity_mappings(self, entity_file="./graph_data/entity_list.txt"):
        """entity_list.txt에서 노드 ID 매핑 로드"""
        with open(entity_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) == 3:
                        name, node_id, node_type = parts[0], int(parts[1]), parts[2]
                        key = f"{node_type}_{name}"
                        self.node_id_mapping[key] = node_id
    
    def load_scale_trait_mapping(self, mapping_file="./graph_data/scale_trait_mapping.txt"):
        """척도-특성 매핑 로드"""
        self.scale_trait_mapping = {}
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) == 2:
                        scale, trait = parts[0], parts[1]
                        if scale not in self.scale_trait_mapping:
                            self.scale_trait_mapping[scale] = []
                        self.scale_trait_mapping[scale].append(trait)
    
    def load_relation_mappings(self, relation_file="./graph_data/relation_list.txt"):
        """관계 매핑 로드"""
        self.relation_mappings = {}
        with open(relation_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) == 2:
                        relation_name, relation_id = parts[0], int(parts[1])
                        self.relation_mappings[relation_name] = relation_id
    
    def _get_node_id(self, node_name, node_type):
        """노드 이름과 타입으로 ID 조회"""
        key = f"{node_type}_{node_name}"
        if key in self.node_id_mapping:
            return self.node_id_mapping[key]
        elif node_type == 'user':
            new_id = self.current_node_id
            self.node_id_mapping[key] = new_id
            self.current_node_id += 1
            return new_id
        else:
            return None
    
    def load_product_data(self, csv_path):
        """상품 데이터 로드"""
        df = pd.read_csv(csv_path)
        return df
    
    
    def create_trait_nodes(self):
        """Trait 노드 생성"""
        traits = []
        for key, node_id in self.node_id_mapping.items():
            if key.startswith('trait_'):
                trait_name = key.replace('trait_', '')
                self.graph.add_node(node_id, name=trait_name, type='trait')
                self.node_types['trait'].append(node_id)
                traits.append(trait_name)
        
        return traits
    
    def create_concept_nodes(self):
        """Concept 노드 생성"""
        concepts = []
        for key, node_id in self.node_id_mapping.items():
            if key.startswith('concept_'):
                concept_name = key.replace('concept_', '')
                self.graph.add_node(node_id, name=concept_name, type='concept')
                self.node_types['concept'].append(node_id)
                concepts.append(concept_name)
        
        return concepts
    
    def create_item_nodes(self, product_df):
        """Item 노드 생성"""
        for idx, row in product_df.iterrows():
            product_id = row.get('product_id', f"item_{idx}")
            node_id = self._get_node_id(product_id, 'item')
            
            self.graph.add_node(node_id, 
                              name=row.get('name', ''),
                              price=row.get('price', 0),
                              category=row.get('category', ''),
                              type='item',
                              original_id=product_id)
            self.node_types['item'].append(node_id)
    
    def add_user_from_psychology_test(self, user_id, psychology_results):
        """심리테스트 결과로 User 노드 동적 생성"""
        node_id = self._get_node_id(user_id, 'user')
        self.graph.add_node(node_id, 
                          name=user_id,
                          type='user',
                          original_id=user_id)
        self.node_types['user'].append(node_id)
        
        for scale, result in psychology_results.items():
            if scale in self.scale_trait_mapping:
                for trait in self.scale_trait_mapping[scale]:
                    trait_id = self._get_node_id(trait, 'trait')
                    if trait_id in [n for n in self.graph.nodes() if self.graph.nodes[n].get('type') == 'trait']:
                        weight = result.get('score', result.get('average', 0.5))
                        self.graph.add_edge(node_id, trait_id, 
                                          relation='user_trait', 
                                          weight=weight)
        
        return node_id
    
    def load_trait_concept_weights(self, weights_file="./graph_data/trait_concept_weights.txt"):
        """Trait-Concept 가중치 파일에서 엣지 로드"""
        with open(weights_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) == 3:
                        trait_id, concept_id, weight = int(parts[0]), int(parts[1]), float(parts[2])
                        if trait_id in self.graph.nodes() and concept_id in self.graph.nodes():
                            self.graph.add_edge(trait_id, concept_id,
                                              relation='trait_concept',
                                              weight=weight)
    
    def build_base_knowledge_graph(self, product_csv_path):
        """기본 지식 그래프 구축"""
        product_df = self.load_product_data(product_csv_path)
        
        traits = self.create_trait_nodes()
        concepts = self.create_concept_nodes()
        self.create_item_nodes(product_df)
        
        self.load_trait_concept_weights()
        
        return self.graph
    
    def print_graph_info(self):
        """그래프 정보 출력"""
        print(f"노드: {self.graph.number_of_nodes()}, 엣지: {self.graph.number_of_edges()}")
        for node_type, nodes in self.node_types.items():
            print(f"{node_type}: {len(nodes)}")
    
    def save_graph_files(self, output_dir="./graph_data"):
        """그래프를 표준 txt 파일들로 저장"""
        import os
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Entity List 업데이트 (실제 아이템 정보 포함)
        entity_file = os.path.join(output_dir, "entity_list.txt")
        with open(entity_file, 'w', encoding='utf-8') as f:
            f.write("# Entity List - Node ID Mapping\n")
            f.write("# Format: original_id remap_id node_type\n\n")
            
            for node_id in self.graph.nodes():
                node_data = self.graph.nodes[node_id]
                original_id = node_data.get('name', f"node_{node_id}")
                node_type = node_data.get('type', 'unknown')
                f.write(f"{original_id} {node_id} {node_type}\n")
        
        # 2. Graph Edges 생성
        edges_file = os.path.join(output_dir, "graph_edges.txt")
        with open(edges_file, 'w', encoding='utf-8') as f:
            f.write("# Graph Edges (Triples)\n")
            f.write("# Format: head_id relation_id tail_id weight\n\n")
            
            for head, tail, edge_data in self.graph.edges(data=True):
                relation = edge_data.get('relation', 'unknown')
                weight = edge_data.get('weight', 1.0)
                
                # 관계 타입을 ID로 매핑
                relation_id = self.relation_mappings.get(relation, 0)
                
                f.write(f"{head} {relation_id} {tail} {weight}\n")
        
        pass
    
    def save_graph(self, save_path):
        """기존 pickle 저장 (호환성 유지)"""
        graph_data = {
            'graph': self.graph,
            'node_types': self.node_types,
            'node_id_mapping': self.node_id_mapping
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(graph_data, f)

def main():
    product_csv = "../../Present-Data-Generation/dataset/products_with_description.csv"
    
    graph_gen = GraphGenerator()
    graph = graph_gen.build_base_knowledge_graph(product_csv)
    
    test_psychology = {
        'Big-Five': {'score': 4.2},
        'CNFU': {'score': 3.8},
        'CVPA': {'score': 4.5},
        'MSV': {'score': 2.9},
        'SSS': {'score': 3.6}
    }
    
    user_node_id = graph_gen.add_user_from_psychology_test("test_user_001", test_psychology)
    graph_gen.print_graph_info()
    
    graph_gen.save_graph_files("./graph_data")
    graph_gen.save_graph("./recommendation_graph.pkl")

if __name__ == "__main__":
    main()