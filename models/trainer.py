"""
그래프 임베딩 모델 학습 및 관리
"""

import sys
import os
import time
from pathlib import Path
import pickle
import numpy as np

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import (
    GRAPH_PKL_PATH, MODEL_CONFIG, PROJECT_ROOT,
    ensure_directories
)
from models.graph_embedding import GraphEmbeddingModel

class GraphTrainer:
    """그래프 임베딩 모델 학습 관리자"""
    
    def __init__(self, config=None):
        self.config = config or MODEL_CONFIG
        self.model = GraphEmbeddingModel(self.config)
        self.embeddings_save_path = PROJECT_ROOT / "models" / "embeddings.pkl"
        
        # 디렉토리 생성
        ensure_directories()
        
    def load_graph_data(self):
        """그래프 데이터 로드"""
        print("=== 그래프 데이터 로드 ===")
        
        if not GRAPH_PKL_PATH.exists():
            print(f"❌ 그래프 파일이 없습니다: {GRAPH_PKL_PATH}")
            print("먼저 data/graph_gen.py를 실행하여 그래프를 생성하세요.")
            return False
        
        try:
            self.model.load_graph(GRAPH_PKL_PATH)
            return True
        except Exception as e:
            print(f"❌ 그래프 로드 실패: {e}")
            return False
    
    def train_embeddings(self):
        """그래프 임베딩 학습"""
        print("\n=== 그래프 임베딩 학습 ===")
        
        start_time = time.time()
        
        # Node2Vec 임베딩 학습
        embeddings = self.model.train_embeddings(
            dimensions=self.config["embedding_dim"],
            walk_length=30,
            num_walks=200,
            workers=4
        )
        
        training_time = time.time() - start_time
        print(f"✅ 임베딩 학습 완료! 소요시간: {training_time:.2f}초")
        
        return embeddings
    
    def save_model(self):
        """학습된 모델 저장"""
        print(f"\n=== 모델 저장 ===")
        
        try:
            self.model.save_embeddings(self.embeddings_save_path)
            print(f"✅ 모델 저장 완료: {self.embeddings_save_path}")
            return True
        except Exception as e:
            print(f"❌ 모델 저장 실패: {e}")
            return False
    
    def load_model(self):
        """저장된 모델 로드"""
        print("=== 학습된 모델 로드 ===")
        
        if not self.embeddings_save_path.exists():
            print(f"❌ 저장된 모델이 없습니다: {self.embeddings_save_path}")
            return False
        
        try:
            # 그래프 먼저 로드
            if not self.load_graph_data():
                return False
            
            # 임베딩 로드
            self.model.load_embeddings(self.embeddings_save_path)
            print("✅ 모델 로드 완료!")
            return True
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            return False
    
    def evaluate_embeddings(self):
        """임베딩 품질 평가"""
        print("\n=== 임베딩 품질 평가 ===")
        
        if not self.model.node_embeddings:
            print("❌ 임베딩이 없습니다. 먼저 학습을 진행하세요.")
            return
        
        # 기본 통계
        embeddings = list(self.model.node_embeddings.values())
        embeddings_array = np.array(embeddings)
        
        print(f"📊 임베딩 통계:")
        print(f"  - 노드 수: {len(embeddings)}")
        print(f"  - 임베딩 차원: {embeddings_array.shape[1]}")
        print(f"  - 평균 norm: {np.mean(np.linalg.norm(embeddings_array, axis=1)):.4f}")
        print(f"  - 표준편차: {np.std(embeddings_array):.4f}")
        
        # 노드 타입별 통계
        if hasattr(self.model, 'node_types'):
            print(f"\n📈 노드 타입별 분포:")
            for node_type, nodes in self.model.node_types.items():
                count = len([n for n in nodes if n in self.model.node_embeddings])
                print(f"  - {node_type}: {count}개")
    
    def test_similarity(self, node1=None, node2=None, top_k=5):
        """노드 간 유사도 테스트"""
        print(f"\n=== 유사도 테스트 ===")
        
        if not self.model.node_embeddings:
            print("❌ 임베딩이 없습니다.")
            return
        
        # 테스트할 노드 선택
        if node1 is None:
            # 랜덤하게 Concept 노드 선택
            concept_nodes = self.model.node_types.get('concept', [])
            if concept_nodes:
                node1 = concept_nodes[0]
            else:
                node1 = list(self.model.node_embeddings.keys())[0]
        
        if node1 not in self.model.node_embeddings:
            print(f"❌ 노드 {node1}의 임베딩이 없습니다.")
            return
        
        # 모든 노드와의 유사도 계산
        from sklearn.metrics.pairwise import cosine_similarity
        
        target_embedding = self.model.node_embeddings[node1]
        similarities = []
        
        for node_id, embedding in self.model.node_embeddings.items():
            if node_id != node1:
                similarity = cosine_similarity(
                    target_embedding.reshape(1, -1),
                    embedding.reshape(1, -1)
                )[0][0]
                
                # 노드 정보 가져오기
                node_data = self.model.graph.nodes[node_id]
                node_name = node_data.get('name', str(node_id))
                node_type = node_data.get('type', 'unknown')
                
                similarities.append({
                    'node_id': node_id,
                    'node_name': node_name,
                    'node_type': node_type,
                    'similarity': similarity
                })
        
        # 유사도 순 정렬
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 결과 출력
        node_data = self.model.graph.nodes[node1]
        node_name = node_data.get('name', str(node1))
        node_type = node_data.get('type', 'unknown')
        
        print(f"🎯 기준 노드: {node_name} ({node_type})")
        print(f"📋 가장 유사한 {top_k}개 노드:")
        
        for i, sim in enumerate(similarities[:top_k], 1):
            print(f"  {i}. {sim['node_name']} ({sim['node_type']}) - 유사도: {sim['similarity']:.4f}")
    
    def full_training_pipeline(self):
        """전체 학습 파이프라인 실행"""
        print("🚀 그래프 임베딩 전체 학습 파이프라인 시작!")
        print("=" * 60)
        
        # 1. 그래프 데이터 로드
        if not self.load_graph_data():
            return False
        
        # 2. 임베딩 학습
        embeddings = self.train_embeddings()
        if not embeddings:
            return False
        
        # 3. 모델 저장
        if not self.save_model():
            return False
        
        # 4. 품질 평가
        self.evaluate_embeddings()
        
        # 5. 유사도 테스트
        self.test_similarity()
        
        print("\n" + "=" * 60)
        print("✅ 전체 학습 파이프라인 완료!")
        print(f"💾 저장된 모델: {self.embeddings_save_path}")
        
        return True

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='그래프 임베딩 모델 학습')
    parser.add_argument('--mode', choices=['train', 'load', 'test'], 
                       default='train', help='실행 모드')
    parser.add_argument('--test-node', type=str, help='유사도 테스트할 노드 ID')
    
    args = parser.parse_args()
    
    trainer = GraphTrainer()
    
    if args.mode == 'train':
        # 전체 학습 파이프라인
        trainer.full_training_pipeline()
        
    elif args.mode == 'load':
        # 저장된 모델 로드 및 평가
        if trainer.load_model():
            trainer.evaluate_embeddings()
            trainer.test_similarity()
        
    elif args.mode == 'test':
        # 유사도 테스트만
        if trainer.load_model():
            if args.test_node:
                trainer.test_similarity(node1=int(args.test_node))
            else:
                trainer.test_similarity()

if __name__ == "__main__":
    main()