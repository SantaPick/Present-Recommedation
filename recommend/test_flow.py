"""
심리테스트 기반 선물 추천 시스템 전체 플로우 테스트
"""

import random
import pandas as pd
import numpy as np
import sys
import os

# 상대경로로 프로젝트 경로 추가
sys.path.append('../')
sys.path.append('../../')

def step1_user_input():
    """1단계: 개인 정보 입력"""
    print("=== 1단계: 개인 정보 입력 ===")
    
    user_info = {
        'name': '김테스트',
        'gender': '여성',
        'age': 25
    }
    
    print(f"사용자: {user_info['name']} ({user_info['gender']}, {user_info['age']}세)")
    return user_info

def step2_psychology_test():
    """2단계: 심리테스트 진행 (시뮬레이션)"""
    print("\n=== 2단계: 심리테스트 진행 ===")
    
    # 척도별 랜덤 점수 생성
    results = {}
    scales = ['Big-Five', 'CNFU', 'CVPA', 'MSV', 'SSS']
    
    for scale in scales:
        score = random.uniform(2.0, 5.0)
        level = 'High' if score >= 4 else 'Medium' if score >= 3 else 'Low'
        
        results[scale] = {
            'score': score,
            'level': level
        }
        
        print(f"{scale}: {score:.2f}점 ({level})")
    
    return results

def step3_recommendation(psychology_results):
    """3단계: 선물 추천 결과 생성"""
    print("\n=== 3단계: 선물 추천 결과 ===")
    
    # 가상의 상품들
    sample_products = [
        {'name': '프리미엄 향수 세트', 'price': 120000, 'category': '뷰티'},
        {'name': '한정판 디자이너 가방', 'price': 350000, 'category': '패션'},
        {'name': '아트 포스터 컬렉션', 'price': 45000, 'category': '인테리어'},
        {'name': '수제 초콜릿 박스', 'price': 65000, 'category': '식품'},
        {'name': '블루투스 프리미엄 스피커', 'price': 180000, 'category': '전자기기'}
    ]
    
    # 심리테스트 결과 기반 추천 점수 계산 (간단한 규칙)
    recommendations = []
    
    for product in sample_products:
        score = random.uniform(3.0, 5.0)  # 기본 점수
        reasons = []
        
        # CNFU가 높으면 한정판 선호
        if psychology_results['CNFU']['level'] == 'High' and '한정' in product['name']:
            score += 1.0
            reasons.append("독특함 추구 성향")
        
        # CVPA가 높으면 디자인/뷰티 선호
        if psychology_results['CVPA']['level'] == 'High' and product['category'] in ['뷰티', '패션']:
            score += 0.8
            reasons.append("미적 감각")
        
        # Big-Five가 높으면 프리미엄 선호
        if psychology_results['Big-Five']['level'] == 'High' and product['price'] > 100000:
            score += 0.5
            reasons.append("프리미엄 선호")
        
        if not reasons:
            reasons.append("종합적 선호도")
        
        recommendations.append({
            'product': product,
            'score': score,
            'reasons': reasons
        })
    
    # 점수 순 정렬
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    print("🎁 추천 결과 (Top 5):")
    for i, rec in enumerate(recommendations, 1):
        product = rec['product']
        print(f"{i}. {product['name']} - {product['price']:,}원")
        print(f"   점수: {rec['score']:.2f}, 이유: {', '.join(rec['reasons'])}")
    
    return recommendations

def step4_visualization(psychology_results, recommendations):
    """4단계: 근거 시각화 (간단 출력)"""
    print("\n=== 4단계: 근거 시각화 ===")
    
    print("📊 심리적 특성 프로필:")
    for scale, result in psychology_results.items():
        bar = "█" * int(result['score'])
        print(f"{scale:10}: {bar} ({result['score']:.2f})")
    
    print(f"\n🎯 추천 근거:")
    top_product = recommendations[0]['product']
    top_reasons = recommendations[0]['reasons']
    print(f"1위 '{top_product['name']}'가 추천된 이유:")
    for reason in top_reasons:
        print(f"  • {reason}")

def step5_graph_integration(user_info, psychology_results):
    """5단계: 지식 그래프 연동 (실제 구현 예시)"""
    print("\n=== 5단계: 지식 그래프 연동 ===")
    
    # 실제로는 graph_gen.py의 KnowledgeGraphGenerator 사용
    print("📊 기본 지식 그래프 로드...")
    print("👤 사용자 노드 동적 생성...")
    
    # 심리테스트 결과를 그래프에 반영
    user_id = f"user_{user_info['name']}"
    print(f"🔗 {user_id} → Trait 엣지 생성:")
    
    for scale, result in psychology_results.items():
        score = result['score']
        level = result['level']
        print(f"   • {scale}: {score:.2f} ({level})")
    
    print("🎯 그래프 기반 추천 알고리즘 실행...")
    print("✅ 개인화된 추천 결과 생성 완료!")

def main():
    """전체 플로우 실행"""
    print("🎁 심리테스트 기반 선물 추천 시스템 🎁")
    print("=" * 50)
    
    # 전체 플로우 실행
    user_info = step1_user_input()
    psychology_results = step2_psychology_test()
    recommendations = step3_recommendation(psychology_results)
    step4_visualization(psychology_results, recommendations)
    step5_graph_integration(user_info, psychology_results)
    
    print(f"\n✨ {user_info['name']}님의 맞춤 추천 완료! ✨")

if __name__ == "__main__":
    main()
