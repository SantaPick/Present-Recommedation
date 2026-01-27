# Present-Recommedation

## 프로젝트 구조

```
Present-Recommedation/
├── data/
│   ├── graph_data/
│   │   ├── entity_list.txt
│   │   ├── relation_list.txt
│   │   └── trait_concept_weights.txt
│   ├── product/
│   │   ├── images/
│   │   │   ├── [product_id]/
│   │   │   └── [product_id]_main.[jpg|png|jpeg]
│   │   └── products_with_description_filtered.csv
│   ├── graph_gen.py
│   ├── loader.py
│   └── preprocessor.py
├── docs/
│   ├── evaluation_strategy.md
│   ├── graph_recommendation_plan.md
│   ├── node_design_analysis.md
│   ├── persona_gt_generator.py
│   ├── reference_analysis.md
│   ├── strategy.md
│   └── vector_db_analysis.md
├── models/
│   ├── checkpoints/
│   ├── evaluator.py
│   ├── graphsage.py
│   ├── kgat.py
│   └── trainer.py
├── recommend/
│   ├── engine.py
│   ├── test_flow.py
│   └── test_recommendation_flow.ipynb
├── utils/
│   ├── config.py
│   └── logger.py
├── LICENSE
├── README.md
└── requirements.txt
```
