# 모델 훈련 방법

## 훈련 실행

```bash
python models/trainer.py --mode train
```

## 생성되는 파일

- `models/embeddings.pkl`: 훈련된 Node2Vec 임베딩

## 훈련 과정

1. 그래프 데이터 로드 (`data/recommendation_graph.pkl`)
2. Node2Vec 모델 훈련 (차원: 128, walk_length: 80, num_walks: 10)
3. 임베딩 저장

## 테스트

```bash
python models/trainer.py --mode test
```