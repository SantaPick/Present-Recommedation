"""
Item-Concept 가중치 파일 생성 스크립트
products_with_concepts.csv에서 concept 점수를 읽어와 가중치 파일 생성
"""

import pandas as pd
import os

def generate_item_concept_weights():
    # CSV 파일 경로
    csv_path = "../product/products_with_concepts.csv"
    output_path = "./item_concept_weights.txt"
    
    # CSV 파일 로드
    df = pd.read_csv(csv_path)
    
    # Concept 컬럼들 (숫자 점수가 있는 컬럼들만)
    concept_columns = {
        '유니크': 300,      # unique
        '차분함': 301,      # calm  
        '심플함': 302,      # simple
        '의미적가치': 303,   # meaningful
        '고급스러움': 304,   # luxury
        '효율성': 305,      # efficiency
        '오락성': 306,      # entertainment
        '휴식': 307,        # relaxation
        '환경/사회가치': 308, # eco_social
        '채도': 312,        # saturation
        '색온도': 313,      # brightness (색온도->명도로 매핑)
        '재질감도': 309,     # soft_hard
        '표면감': 310,      # rough_smooth
    }
    
    # 가중치 파일 생성
    with open(output_path, 'w', encoding='utf-8') as f:
        item_id_start = 1000  # Item 노드 ID 시작 번호
        
        for idx, row in df.iterrows():
            item_id = item_id_start + idx
            
            for concept_col, concept_id in concept_columns.items():
                if concept_col in df.columns:
                    score = row[concept_col]
                    if pd.notna(score) and score != 'X':
                        # 1-5 점수를 0-1 범위로 정규화
                        normalized_weight = (float(score) - 1) / 4
                        f.write(f"{item_id} {concept_id} {normalized_weight:.2f}\n")
    
    print(f"Item-Concept 가중치 파일이 생성되었습니다: {output_path}")
    print(f"총 {len(df)}개 상품 처리 완료")

if __name__ == "__main__":
    generate_item_concept_weights()