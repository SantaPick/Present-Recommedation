import pandas as pd
import os

# 파일 경로 설정
ENTITY_LIST_PATH = "entity_list.txt"
ITEM_CONCEPTS_CSV = "Item_Concepts_Weight.csv"
ITEM_TRAIT_CSV = "Item-Trait-Weight.csv"
TRAIT_CONCEPT_CSV = "Trait-Concept-Weight.xlsx.csv"

# 출력 파일 경로
ITEM_CONCEPT_TXT = "item_concept_weights.txt"
ITEM_TRAIT_TXT = "item_trait_weights.txt"
TRAIT_CONCEPT_TXT = "Trait_Concept_Weight.txt"

def load_entity_mapping():
    """entity_list.txt에서 노드 이름과 ID 매핑 생성, 타입별로 분류"""
    entity_to_id = {}
    traits = []
    concepts = []
    items = []
    
    with open(ENTITY_LIST_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    node_id = parts[1]
                    entity_type = parts[2]
                    
                    entity_to_id[name] = node_id
                    
                    if entity_type == 'trait':
                        traits.append(name)
                    elif entity_type == 'concept':
                        concepts.append(name)
                    elif entity_type == 'item':
                        items.append(name)
    
    return entity_to_id, traits, concepts, items

def generate_item_concept_weights():
    """Item_Concepts_Weight.csv를 기반으로 item_concept_weights.txt 생성"""
    print("item_concept_weights.txt 생성 중...")
    
    entity_to_id, traits, concepts, items = load_entity_mapping()
    df = pd.read_csv(ITEM_CONCEPTS_CSV)
    
    with open(ITEM_CONCEPT_TXT, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            product_id = str(row['product_id'])
            item_node_id = entity_to_id.get(product_id)
            
            if item_node_id:
                # CSV에 있는 concept 컬럼들 중 entity_list에 있는 것만 처리
                for concept in concepts:
                    if concept in row and pd.notna(row[concept]):
                        concept_node_id = entity_to_id.get(concept)
                        if concept_node_id:
                            weight = float(row[concept]) / 5.0  # 1-5 스케일을 0-1로 정규화
                            f.write(f"{item_node_id} {concept_node_id} {weight:.2f}\n")
    
    print(f"{ITEM_CONCEPT_TXT} 생성 완료")

def generate_item_trait_weights():
    """Item-Trait-Weight.csv를 기반으로 item_trait_weights.txt 생성"""
    print("item_trait_weights.txt 생성 중...")
    
    entity_to_id, traits, concepts, items = load_entity_mapping()
    df = pd.read_csv(ITEM_TRAIT_CSV)
    
    with open(ITEM_TRAIT_TXT, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            product_id = str(row['product_id'])
            item_node_id = entity_to_id.get(product_id)
            
            if item_node_id:
                # CSV에 있는 trait 컬럼들 중 entity_list에 있는 것만 처리
                for trait in traits:
                    if trait in row and pd.notna(row[trait]):
                        trait_node_id = entity_to_id.get(trait)
                        if trait_node_id:
                            weight = float(row[trait])
                            f.write(f"{item_node_id} {trait_node_id} {weight:.2f}\n")
    
    print(f"{ITEM_TRAIT_TXT} 생성 완료")

def generate_trait_concept_weights():
    """Trait-Concept-Weight.xlsx.csv를 기반으로 Trait_Concept_Weight.txt 생성"""
    print("Trait_Concept_Weight.txt 생성 중...")
    
    entity_to_id, traits, concepts, items = load_entity_mapping()
    df = pd.read_csv(TRAIT_CONCEPT_CSV)
    
    with open(TRAIT_CONCEPT_TXT, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            trait_name = row['Trait']
            trait_node_id = entity_to_id.get(trait_name)
            
            if trait_node_id:
                # Trait 컬럼을 제외한 컬럼들 중 entity_list에 있는 concept만 처리
                for concept_name in df.columns[1:]:  # 첫 번째 컬럼(Trait) 제외
                    if concept_name in concepts and pd.notna(row[concept_name]):
                        concept_node_id = entity_to_id.get(concept_name)
                        if concept_node_id:
                            weight = float(row[concept_name])
                            f.write(f"{trait_node_id} {concept_node_id} {weight:.2f}\n")
    
    print(f"{TRAIT_CONCEPT_TXT} 생성 완료")

def delete_old_files():
    """기존 구버전 파일들 삭제"""
    old_files = [ITEM_CONCEPT_TXT, ITEM_TRAIT_TXT, TRAIT_CONCEPT_TXT]
    
    for file_path in old_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ 기존 파일 삭제: {file_path}")

def main():
    print("=== 그래프 가중치 파일 업데이트 시작 ===")
    
    # 1. 기존 파일 삭제
    delete_old_files()
    
    # 2. 새 파일들 생성
    generate_item_concept_weights()
    generate_item_trait_weights()
    generate_trait_concept_weights()
    
    print("\n=== 모든 작업 완료 ===")

if __name__ == "__main__":
    main()