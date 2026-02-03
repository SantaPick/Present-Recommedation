"""
entity_list.txt에 Item 노드들 추가하는 스크립트
products_with_concepts.csv에서 상품 정보를 읽어와 Item 노드로 추가
"""

import pandas as pd

def add_item_entities():
    csv_path = "../product/products_with_concepts.csv"
    entity_file = "./entity_list.txt"
    
    # CSV 파일 로드
    df = pd.read_csv(csv_path)
    
    # 기존 entity_list.txt 읽기
    with open(entity_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # Item 노드들 추가
    with open(entity_file, 'a', encoding='utf-8') as f:
        item_id_start = 1000
        
        for idx, row in df.iterrows():
            item_id = item_id_start + idx
            product_id = row['product_id']
            f.write(f"{product_id} {item_id} item\n")
    
    print(f"entity_list.txt에 {len(df)}개 Item 노드 추가 완료")

if __name__ == "__main__":
    add_item_entities()